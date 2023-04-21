"""Bumpversion bumper."""
import re
from typing import Any, Dict, List

import semver


class SemVerBumper:
    """Bump version according to SemVer."""

    def __init__(self, options: Dict[str, Any]):
        self.options = options

    def __call__(self, version: Dict[str, Any], bumped_parts: List[str]) -> Dict[str, Any]:
        """Bump version specified by options."""
        parsed_version = semver.Version(**version)
        for part in bumped_parts:
            if part in ("prerelease", "build"):
                parsed_version = getattr(parsed_version, "bump_" + part)(
                    token=self.options.get(part + "_token", None)
                )
            else:
                parsed_version = parsed_version.next_version(part)
        return parsed_version.to_dict()


class RegexBumper:
    """Bump version string defined by a regex group."""

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
        for part in bumped_parts:
            parsed_version = version.get(part)
            if parsed_version is None:
                version[part] = "1"
            else:
                version[part] = self._increase_number(parsed_version)
            # Set the rest of the parts to nulls
            bumped_index = list(version).index(part)
            keys_to_null = list(version)[bumped_index + 1 :]
            for key in keys_to_null:
                if version[key].isnumeric():
                    version[key] = "0"
                else:
                    # We cannot sensibly null nonnumeric part, delete it
                    del version[key]

        return version
