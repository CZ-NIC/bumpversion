"""Version parsers."""
import re
from re import Pattern
from typing import Union, cast

import semver


class RegexParser:
    """Parse version by regular expression.

    Returns:
        Dictionary with named capture groups.
    """

    def __init__(self, regex: Union[str, Pattern]) -> None:
        self.regex = regex

    def __call__(self, version: str) -> dict:
        """Perform the actual parsing."""
        if matches := re.fullmatch(self.regex, version):
            return matches.groupdict()
        else:
            raise ValueError(f"Version {version} does not match regex {self.regex}")


class PEP440Parser(RegexParser):
    """Regex based PEP440 parser."""

    def __init__(self) -> None:
        regex = re.compile(
            r"(?:(?P<epoch>\d+)!)?"  # Epoch segment: N!
            r"(?P<major>\d+)(?:\.(?P<minor>\d+)(?:\.(?P<micro>\d+))?)?"  # Release segment: N(.N)*
            r"(?:[-._]?(?:(?:a|alpha)(?P<alpha>\d+)|(?:b|beta)(?P<beta>\d+)|(?:rc|c|pre|preview)(?P<rc>\d+)))?"  # Pre-release segment: {a|b|rc}N # noqa: E501
            r"(?:[-._]?(?:post|r|rev)(?P<post>\d+))?"  # Post-release segment: .postN
            r"(?:[-._]?(?:dev)(?P<dev>\d*))?"  # Development release segment: .devN
            r"(?:\+(?P<local>.+))?"  # Local version label
        )

        super().__init__(regex=regex)

    def __call__(self, version: str) -> dict:
        """Parese version and perform some PEP440 defined normalizations."""
        parsed = super().__call__(version)
        if parsed["dev"] == "":
            parsed["dev"] = "0"
        result = {}
        for part, value in parsed.items():
            if parsed[part] is not None:
                if part != "local":
                    # All public parts should be normalized to numbers
                    result[part] = str(int(value))
                else:
                    result[part] = value
        return result


class SemVerParser:
    """Semantic versioning parser."""

    def __call__(self, version: str) -> dict:
        """Parse SemVer version."""
        return cast(dict, semver.Version.parse(version).to_dict())
