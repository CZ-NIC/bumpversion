"""Bumpversion serializers."""
import itertools
from string import Formatter
from typing import Any, List, Mapping, Sequence, Set, Union

import semver


class StrictFormatter(Formatter):
    """Strict formatter.

    Raises ValueError in case of unused kwargs.
    """

    def check_unused_args(
        self,
        used_args: Set[Union[int, str]],
        args: Sequence[Any],
        kwargs: Mapping[str, Any],
    ) -> None:
        """Check that all args were used when filling format."""
        if set(kwargs.keys()) > used_args:
            raise TypeError("Too many arguments for format")


class FormatSerializer:
    """Serialize version using python `format`."""

    def __init__(self, formats: List[str]):
        self.formatter = StrictFormatter()
        self.formats = formats

    def __call__(self, version: dict, /) -> str:
        """Serialize using python `format`.

        Try each format until you find one that can be filled with provided kwargs.
        Then check that all provided kwargs that weren't None were actually used.
        """
        version_dict = {k: v for k, v in version.items() if v is not None}
        for format in self.formats:
            try:
                return self.formatter.format(format, **version_dict)
            except (KeyError, TypeError):
                pass
        raise ValueError("Version cannot be serialized")


class PEP440Serializer(FormatSerializer):
    """PEP440 format serializer."""

    def __init__(self) -> None:
        formats = [
            "".join(v)
            for v in itertools.product(
                ("{epoch}!", ""),
                ("{major}.{minor}.{micro}", "{major}.{minor}", "{major}"),
                ("a{alpha}", "b{beta}", "rc{rc}", ""),
                (".post{post}", ""),
                (".dev{dev}", ""),
                ("+{local}", ""),
            )
        ]
        super().__init__(formats=formats)


class SemVerSerializer:
    """SemVer serializer."""

    def __call__(self, version: dict, /) -> str:
        """Serialize SemVer version."""
        return str(semver.Version(**version))
