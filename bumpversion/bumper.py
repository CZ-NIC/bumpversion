"""Bumpversion bumper."""
import re
from typing import Any, Dict, List, Optional, TypedDict

import semver


class SemVerBumper:
    """Bump version according to SemVer."""

    def __init__(
        self, *, build_token: Optional[str] = None, prerelease_token: Optional[str] = None
    ):
        self.build_token = build_token
        self.prerelease_token = prerelease_token

    def __call__(self, version: Dict[str, Any], bumped_parts: List[str]) -> Dict[str, Any]:
        """Bump version specified by options."""
        parsed_version = semver.Version(**version)
        for part in bumped_parts:
            if part in ("prerelease", "build"):
                parsed_version = getattr(parsed_version, "bump_" + part)(
                    token=getattr(self, part + "_token")
                )
            else:
                parsed_version = parsed_version.next_version(part)
        return parsed_version.to_dict()


class PartsDefinition(TypedDict, total=False):
    """Defines structure of parts for :class:`RegexBumper`."""

    final: bool
    """Makes the part as contained in a final release.

    Defaults to `True`.
    """
    start: int
    """Sets a starting index for a newly bumped version.

    Defaults to `0`.
    """


class RegexBumper:
    """Bump version string defined by a regex group.

    Can be configured using `parts` which is a dictionary with `part` definition as keys
    and values are dictionaries with `final` (bool) and `start` (int) as keys.

    If a definition for a part is missing, it is assumed as `final` and starting at `0`.

    Parts not defined as final are ommited if their values should be zero and no following
    part has a value.

    The following configuration sets `micro` version as ommited from from final release
    and sets start value for `rc` to `1` (and ommited as well).

    .. code-block:: toml

       [tool.bumpversion.bumper]
       cls = "bumpversion.RegexBumper"

       [tool.bumpversion.bumper.parts]
       micro = { final = false }
       rc = { final = false, start = 1}

    Assuming `current_version = 1.0`, the resulting sequence of bumping:

    .. code-block::

        micro rc -> rc -> minor

    would be:

    .. code-block::

        1.0 -> 1.0.1rc1 -> 1.0.1rc2 -> 1.1
    """

    def __init__(self, *, parts: Optional[Dict[str, PartsDefinition]] = None):
        self.parts = parts or {}

    @staticmethod
    def _increase_number(version: str) -> str:
        regex = re.compile(r"(?P<string>[-._]?\D+)(?P<num>\d+)")
        if version.isnumeric():
            return str(int(version) + 1)
        else:
            # alphanumeric part, find just the ending number and increase that
            match = re.fullmatch(regex, version)
            if match is not None:
                return match["string"] + str(int(match["num"]) + 1)
        raise ValueError(f"Version part {version} cannot be increased.")

    def __call__(self, version: Dict[str, str], bumped_parts: List[str]) -> Dict[str, str]:
        """Bump version specified in bumped_parts."""
        new_version = version.copy()
        for part in bumped_parts:
            parsed_version = new_version.get(part)
            if parsed_version is None:
                new_version[part] = str(self.parts.get(part, {}).get("start", 1))
            else:
                new_version[part] = self._increase_number(parsed_version)
            # Set the rest of the parts to nulls
            bumped_index = list(new_version).index(part)
            keys_to_null = list(new_version)[bumped_index + 1 :]
            for key in keys_to_null:
                if new_version[key].isnumeric() and self.parts.get(key, {}).get("final", True):
                    new_version[key] = "0"
                else:
                    # Either numeric or not final, delete it
                    del new_version[key]

        return new_version
