"""Command line interface."""
import shlex
from typing import Optional, Tuple

import click
from click import echo as _echo

from bumpversion import __version__
from bumpversion.constants import Verbosity
from bumpversion.settings import Settings
from bumpversion.utils import load_instance
from bumpversion.vcs import AbstractVcs, get_vcs


def echo(
    message: str, verbosity: Verbosity, *, settings: Settings, nl: bool = True, err: bool = False
) -> None:
    """Print message with respect to verbosity level.

    Arguments:
        message: The message to print.
        verbosity: A verbosity level of the message.
        settings: Settings.
        nl: Whether to print newline after message.
        err: Whether to print the message to error output instead.
    """
    if verbosity <= settings._verbosity:
        if settings.dry_run:
            message = "[dry-run] " + message
        _echo(message, nl=nl, err=err)


def _load_settings(ctx: click.Context, param: click.Option, value: str) -> str:
    """Load option defaults from config file."""
    # Use `construct` to skip pydantic validation.
    settings = Settings(config_file=value)
    ctx.default_map = {
        "dry_run": settings.dry_run,
        "allow_dirty": settings.allow_dirty,
        "commit": settings.commit,
        "commit_message": settings.commit_message,
        "commit_args": shlex.join(settings.commit_args),
        "tag": settings.tag,
        "tag_name": settings.tag_name,
        "sign_tags": settings.sign_tags,
        "tag_message": settings.tag_message,
        "current_version": settings.current_version,
    }
    # Return the value back, so the config_file is used properly.
    return value


# TODO: Show effective default loaded from config file.
@click.command()
@click.argument("parts", nargs=-1)
@click.version_option(version=__version__, message="bumpversion %(version)s")
@click.option(
    "-v",
    "--verbosity",
    type=int,
    default=Verbosity.INFO,
    show_default=True,
    help="Set verbosity level.",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Set custom config file.",
    # Load defaults from config file.
    callback=_load_settings,
    is_eager=True,
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Don't write any files, just pretend.",
)
@click.option(
    "--allow-dirty",
    is_flag=True,
    help="Don't abort if working directory is dirty",
)
@click.option(
    "--commit/--no-commit",
    help="Commit to version control",
)
@click.option(
    "-m",
    "--commit-message",
    help="Commit message",
)
@click.option("--commit-args", help="Extra arguments to commit command")
@click.option(
    "--tag/--no-tag",
    help="Create a tag in version control",
)
@click.option("--tag-name", help="Tag name (only works with --tag)")
@click.option("--sign-tags/--no-sign-tags", help="Sign tags if created")
@click.option("--tag-message", help="Tag message")
@click.option("--new-version", help="New version that should be in the files")
@click.option(
    "--current-version",
    help="Version that needs to be updated",
)
def main(
    parts: Tuple[str, ...],
    new_version: str,
    verbosity: Verbosity,
    config_file: Optional[str],
    dry_run: bool,
    allow_dirty: bool,
    commit: bool,
    commit_message: str,
    commit_args: str,
    tag: bool,
    tag_name: str,
    sign_tags: bool,
    tag_message: str,
    current_version: str,
) -> None:
    """Bump the project version."""
    if not parts and not new_version:
        raise click.BadParameter("Either parts or --new-version must be defined.")
    if parts and new_version:
        raise click.BadParameter("Only one of parts or --new-version must be defined.")
    settings = Settings(
        config_file=config_file,
        dry_run=dry_run,
        allow_dirty=allow_dirty,
        commit=commit,
        commit_message=commit_message,
        commit_args=shlex.split(commit_args),
        tag=tag,
        tag_name=tag_name,
        sign_tags=sign_tags,
        tag_message=tag_message,
        current_version=current_version,
    )
    settings._verbosity = verbosity

    echo(f"Parts: {parts}", Verbosity.DEBUG, settings=settings)
    echo(f"New version: {new_version}", Verbosity.DEBUG, settings=settings)
    echo(f"Verbosity: {verbosity}", Verbosity.DEBUG, settings=settings)
    echo(f"Config file: {config_file}", Verbosity.DEBUG, settings=settings)
    echo(f"Settings: {settings}", Verbosity.DEBUG, settings=settings)

    parser = load_instance(
        settings.parser.cls,
        **settings.parser.dict(exclude={"cls"}),
    )
    parsed_current_version = parser(current_version)

    if new_version:
        parsed_new_version = parser(new_version)
    else:
        bumper = load_instance(
            settings.bumper.cls,
            **settings.bumper.dict(exclude={"cls"}),
        )
        serializer = load_instance(
            settings.serializer.cls,
            **settings.serializer.dict(exclude={"cls"}),
        )
        parsed_new_version = bumper(parsed_current_version.copy(), parts)
        new_version = serializer(parsed_new_version)

    echo(f"Parsed new version: {parsed_new_version}", Verbosity.DEBUG, settings=settings)

    vcs = get_vcs()
    # Check dirty
    if vcs and not settings.allow_dirty:
        dirty_files = tuple(vcs.get_dirty_files())
        if dirty_files:
            exit(f"VCS directory not clean: {dirty_files}")

    # Bump files
    for file in settings.file:
        echo(f"Bumping file {file.path}", Verbosity.INFO, settings=settings)
        serializer = load_instance(file.serializer.cls, **file.serializer.dict(exclude={"cls"}))
        replacer = load_instance(file.replacer.cls, **file.replacer.dict(exclude={"cls"}))
        if not settings.dry_run:
            replacer(
                current_version=serializer(parsed_current_version.copy()),
                new_version=serializer(parsed_new_version.copy()),
                **file.dict(exclude={"serializer", "replacer"}),
            )
    # Bump config file, if present
    if settings._config_file:
        echo(f"Bumping file {settings._config_file}", Verbosity.INFO, settings=settings)
        if not settings.dry_run:
            serializer = load_instance(
                settings.serializer.cls, **settings.serializer.dict(exclude={"cls"})
            )
            replacer = load_instance(
                settings.replacer.cls, **settings.replacer.dict(exclude={"cls"})
            )
            replacer(
                current_version=serializer(parsed_current_version.copy()),
                new_version=serializer(parsed_new_version.copy()),
                path=settings._config_file,
            )

    if vcs:
        _handle_vcs(new_version, vcs, settings)


def _handle_vcs(new_version: str, vcs: AbstractVcs, settings: Settings) -> None:
    """Handle operations on VCS."""
    message_context = {"current_version": settings.current_version, "new_version": new_version}
    if settings.commit:
        # Add files to commit.
        for file in settings.file:
            echo(f"Adding {file.path}", Verbosity.INFO, settings=settings)
            if not settings.dry_run:
                vcs.add_file(file.path)
        # Do commit.
        message = settings.commit_message.format(**message_context)
        echo(f"Commiting: {message}", Verbosity.INFO, settings=settings)
        if not settings.dry_run:
            vcs.commit(message, extra_args=settings.commit_args)
    if settings.tag:
        tag_name = settings.tag_name.format(**message_context)
        tag_message = settings.tag_message.format(**message_context)
        echo(f"Tagging {tag_name}", Verbosity.INFO, settings=settings)
        if not settings.dry_run:
            vcs.tag(tag_name, message=tag_message, sign_tags=settings.sign_tags)


if __name__ == "__main__":
    main()
