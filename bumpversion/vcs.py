"""Version control system management."""
import subprocess  # nosec
from pathlib import Path
from typing import Iterable, List


class Git:
    """Git management."""

    def get_dirty_files(self) -> Iterable[bytes]:
        """Generate list of modified files."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
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
