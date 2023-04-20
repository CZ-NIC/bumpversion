"""Command line interface."""
from pathlib import Path

import click
from click import echo as _echo

from bumpversion import __version__
from bumpversion.constants import Verbosity


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


@click.option(
    "--tag/--no-tag",
    default=True,
    show_default=True,
    help="Create a tag in version control",
)
@click.option(
    "--commit/--no-commit",
    default=True,
    show_default=True,
    help="Commit to version control",
)
@click.option(
    "--allow-dirty",
    is_flag=True,
    default=False,
    show_default=True,
    help="Don't abort if working directory is dirty",
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="Don't write any files, just pretend.",
)
@click.option(
    "--config-file", type=click.Path(exists=True, dir_okay=False), help="Set custom config file."
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
    config_file: Path,
    dry_run: bool,
    allow_dirty: bool,
    commit: bool,
    tag: bool,
) -> None:
    """Bump the project version."""
    echo(f"New version: {new_version}", Verbosity.DEBUG, verbosity)
    echo(f"Verbosity: {verbosity}", Verbosity.DEBUG, verbosity)
    echo(f"Config file: {config_file}", Verbosity.DEBUG, verbosity)
    echo(f"Dry run: {dry_run}", Verbosity.DEBUG, verbosity)
    echo(f"Allow dirty: {allow_dirty}", Verbosity.DEBUG, verbosity)
    echo(f"Commit: {commit}", Verbosity.DEBUG, verbosity)
    echo(f"Tag: {tag}", Verbosity.DEBUG, verbosity)


if __name__ == "__main__":
    main()
