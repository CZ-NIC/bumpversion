"""Bumpversion replacers."""
from pathlib import Path
from typing import Any


class SearchReplaceReplacer:
    """Search and replace versions in file."""

    def __init__(
        self,
        search: str = "{current_version}",
        replace: str = "{new_version}",
    ) -> None:
        self.search = search
        self.replace = replace

    def __call__(self, *, path: Path, **kwargs: Any) -> None:
        """Replace version occurences in file."""
        with open(path, "r") as fh:
            file_content = fh.read()

        if not self.search.format(**kwargs) in file_content:
            raise RuntimeError(
                "Pattern {} was not found in file {}".format(self.search.format(**kwargs), path)
            )

        replaced = file_content.replace(
            self.search.format(**kwargs), self.replace.format(**kwargs)
        )

        with open(path, "w") as fh:
            fh.write(replaced)
