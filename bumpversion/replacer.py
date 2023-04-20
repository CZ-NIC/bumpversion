"""Bumpversion replacers."""
from pathlib import Path
from typing import Any


class SearchReplaceReplacer:
    """Search and replace versions in file."""

    def __call__(
        self,
        *,
        path: Path,
        search: str = "{old_version}",
        replace: str = "{new_version}",
        **kwargs: Any
    ) -> None:
        """Replace version occurences in file."""
        with open(path, "r") as fh:
            file_content = fh.read()

        if not search.format(**kwargs) in file_content:
            raise RuntimeError(
                "Pattern {} was not found in file {}".format(search.format(**kwargs), path)
            )

        replaced = file_content.replace(search.format(**kwargs), replace.format(**kwargs))

        with open(path, "w") as fh:
            fh.write(replaced)
