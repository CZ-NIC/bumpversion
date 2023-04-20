"""Command line interface."""
from typing import Optional

import click
from click import echo as _echo

from bumpversion import __version__
from bumpversion.constants import Verbosity
from bumpversion.settings import Settings


def echo(
    message: str, level: Verbosity, verbosity: Verbosity, *, nl: bool = True, err: bool = False
) -> None:
    """Print message with respect to verbosity level.

    Arguments:
        message: The message to print.
        level: A verbosity level of the message.
        verbosity: Verbosity level setting.
        nl: Whether to print newline after message.
        err: Whether to print the message to error output instead.
    """
    if level <= verbosity:
        _echo(message, nl=nl, err=err)


def _load_settings(ctx: click.Context, param: click.Option, value: str) -> None:
    """Load option defaults from config file."""
    settings = Settings(config_file=value)
    ctx.default_map = {
        "dry_run": settings.dry_run,
        "allow_dirty": settings.allow_dirty,
        "commit": settings.commit,
        "tag": settings.tag,
    }


# TODO: Show effective default loaded from config file.
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
) -> None:
    """Bump the project version."""
    echo(f"New version: {new_version}", Verbosity.DEBUG, verbosity)
    echo(f"Verbosity: {verbosity}", Verbosity.DEBUG, verbosity)
    echo(f"Config file: {config_file}", Verbosity.DEBUG, verbosity)
    settings = Settings(
        config_file=config_file, dry_run=dry_run, allow_dirty=allow_dirty, commit=commit, tag=tag
    )
    settings._verbosity = verbosity
    echo(f"Settings: {settings}", Verbosity.DEBUG, settings._verbosity)


if __name__ == "__main__":
    main()
