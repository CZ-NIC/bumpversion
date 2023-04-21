import os
import traceback
from pathlib import Path
from typing import Optional, Sequence, cast
from unittest import TestCase
from unittest.mock import ANY

from click import BaseCommand
from click.testing import CliRunner, Result


class CommandMixin:
    """Mixin for command tests."""

    runner = CliRunner(mix_stderr=False)
    command: BaseCommand

    def invoke(
        self, args: Optional[Sequence[str]] = None, *, repo: Optional[Path] = None
    ) -> Result:
        """Invoke a command and return a result."""
        repo = repo or Path(__file__).parent
        cwd = os.getcwd()
        try:
            os.chdir(repo)
            return self.runner.invoke(self.command, args)
        finally:
            os.chdir(cwd)

    def assertCommandSuccess(
        self,
        args: Optional[Sequence[str]] = None,
        *,
        stdout: str = ANY,
        repo: Optional[Path] = None
    ) -> None:
        """Invoke command and check it succeeded."""
        result = self.invoke(args, repo=repo)

        err_msg = ""
        if result.exc_info:  # pragma: no cover
            err_msg = "Unexpected exception found\n\n{}".format(
                "".join(traceback.format_tb(result.exc_info[2]))
            )
        cast(TestCase, self).assertIsNone(result.exception, msg=err_msg)
        err_msg = "command failed with code {}, stderr: {!r}".format(
            result.exit_code, result.stderr
        )
        cast(TestCase, self).assertEqual(result.exit_code, 0, msg=err_msg)
        cast(TestCase, self).assertEqual(result.stdout, stdout)
        cast(TestCase, self).assertEqual(result.stderr, "")

    def assertCommandFail(
        self,
        args: Optional[Sequence[str]] = None,
        *,
        stdout: str = "",
        stderr: str = "",
        repo: Optional[Path] = None
    ) -> None:
        """Invoke command and check it failed."""
        result = self.invoke(args, repo=repo)

        cast(TestCase, self).assertIsInstance(result.exception, SystemExit)
        cast(TestCase, self).assertNotEqual(result.exit_code, 0)
        cast(TestCase, self).assertEqual(result.stdout, stdout)
        cast(TestCase, self).assertIn(stderr, result.stderr)
