"""Version control system management."""
import subprocess  # nosec
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List, Optional


class AbstractVcs(ABC):
    """Base version control system manager."""

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Return whether version control system is available."""

    @abstractmethod
    def get_dirty_files(self) -> Iterable[str]:
        """Generate list of modified files."""

    @abstractmethod
    def add_file(self, path: Path) -> None:
        """Add file to a version control."""

    @abstractmethod
    def commit(self, message: str, *, extra_args: List[str]) -> None:
        """Make a commit."""

    @abstractmethod
    def tag(self, tag: str, *, message: str, sign_tags: bool) -> None:
        """Make a tag."""


class Git(AbstractVcs):
    """Git manager."""

    @classmethod
    def is_available(cls) -> bool:
        """Return whether version control system is available."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], check=True, stdout=subprocess.DEVNULL
            )  # nosec
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        return True

    def get_dirty_files(self) -> Iterable[str]:
        """Generate list of modified files."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )  # nosec
        for line in result.stdout.splitlines():
            status = line[:2]
            filename = line[3:].strip()
            if status != b"??":
                yield filename

    def add_file(self, path: Path) -> None:
        """Add file to a version control."""
        subprocess.run(["git", "add", path], check=True)  # nosec

    def commit(self, message: str, *, extra_args: List[str]) -> None:
        """Make a commit."""
        subprocess.run(["git", "commit", "--message", message] + extra_args, check=True)  # nosec

    def tag(self, tag: str, *, message: str, sign_tags: bool) -> None:
        """Make a tag."""
        cmd = ["git", "tag", tag, "--message", message]
        if sign_tags:
            cmd += ["--sign"]
        subprocess.run(cmd, check=True)  # nosec


def get_vcs() -> Optional[AbstractVcs]:
    """Return version control system manager to be used or None if none found."""
    for cls in (Git,):
        if cls.is_available():
            return cls()
    return None
