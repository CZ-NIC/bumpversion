"""Command line interface."""
from typing import Optional

import click
from click import echo as _echo

from bumpversion import __version__
from bumpversion.constants import Verbosity
from bumpversion.settings import Settings
from bumpversion.utils import load_instance
from bumpversion.vcs import Git


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


def _load_settings(ctx: click.Context, param: click.Option, value: str) -> None:
    """Load option defaults from config file."""
    settings = Settings(config_file=value)
    ctx.default_map = {
        "dry_run": settings.dry_run,
        "allow_dirty": settings.allow_dirty,
        "commit": settings.commit,
        "tag": settings.tag,
        "current_version": settings.current_version,
    }


# TODO: Show effective default loaded from config file.
@click.option(
    "--current-version",
    help="Version that needs to be updated",
)
@click.option(
    "--tag/--no-tag",
    help="Create a tag in version control",
)
@click.option(
    "--commit/--no-commit",
    help="Commit to version control",
)
@click.option(
    "--allow-dirty",
    is_flag=True,
    help="Don't abort if working directory is dirty",
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Don't write any files, just pretend.",
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
    "-v",
    "--verbosity",
    type=int,
    default=Verbosity.INFO,
    show_default=True,
    help="Set verbosity level.",
)
@click.version_option(version=__version__, message="bumpversion %(version)s")
@click.argument("new-version")
@click.command()
def main(
    new_version: str,
    verbosity: Verbosity,
    config_file: Optional[str],
    dry_run: bool,
    allow_dirty: bool,
    commit: bool,
    tag: bool,
    current_version: str,
) -> None:
    """Bump the project version."""
    settings = Settings(
        config_file=config_file,
        dry_run=dry_run,
        allow_dirty=allow_dirty,
        commit=commit,
        tag=tag,
        current_version=current_version,
    )
    settings._verbosity = verbosity

    parser = load_instance(
        settings.parser.cls,
        **settings.parser.dict(exclude={"cls"}),
    )
    parsed_current_version = parser(current_version)
    parsed_new_version = parser(new_version)

    echo(f"New version: {new_version}", Verbosity.DEBUG, settings=settings)
    echo(f"Verbosity: {verbosity}", Verbosity.DEBUG, settings=settings)
    echo(f"Config file: {config_file}", Verbosity.DEBUG, settings=settings)
    echo(f"Settings: {settings}", Verbosity.DEBUG, settings=settings)

    vcs = Git()
    # Check dirty
    dirty_files = tuple(vcs.get_dirty_files())
    if not settings.allow_dirty and dirty_files:
        exit(f"Git directory not clean: {dirty_files}")

    # Bump files
    for file in settings.file:
        echo(f"Bumping file {file.path}", Verbosity.INFO, settings=settings)
        serializer = load_instance(file.serializer.cls, **file.serializer.dict(exclude={"cls"}))
        replacer = load_instance(file.replacer.cls, **file.replacer.dict(exclude={"cls"}))
        if not settings.dry_run:
            replacer(
                current_version=serializer(parsed_current_version),
                new_version=serializer(parsed_new_version),
                **file.dict(exclude={"serializer", "replacer"}),
            )

    if commit:
        # Add files to commit.
        for file in settings.file:
            echo(f"Adding {file.path}", Verbosity.INFO, settings=settings)
            if not settings.dry_run:
                vcs.add_file(file.path)
        # Do commit.
        message = f"Bump version: {current_version} → {new_version}"
        echo(f"Commiting: {message}", Verbosity.INFO, settings=settings)
        if not settings.dry_run:
            vcs.commit(message)
    if tag:
        echo(f"Tagging {new_version}", Verbosity.INFO, settings=settings)
        if not settings.dry_run:
            vcs.tag(new_version)


if __name__ == "__main__":
    main()
