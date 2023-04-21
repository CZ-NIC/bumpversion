"""Definitions of basic versioning schemas."""
from enum import Enum
from typing import Any, Dict


class Schema(str, Enum):
    """Definiton of allowed version_schemas."""

    semver = "semver"
    pep440 = "pep440"


SCHEMAS = {
    Schema.semver: {
        "bumper": {"cls": "bumpversion.SemVerBumper"},
        "parser": {"cls": "bumpversion.SemVerParser"},
        "serializer": {"cls": "bumpversion.SemVerSerializer"},
        "replacer": {"cls": "bumpversion.SearchReplaceReplacer"},
    },
    Schema.pep440: {
        "bumper": {"cls": "bumpversion.RegexBumper"},
        "parser": {"cls": "bumpversion.PEP440Parser"},
        "serializer": {"cls": "bumpversion.PEP440Serializer"},
        "replacer": {"cls": "bumpversion.SearchReplaceReplacer"},
    },
}


def get_schema(schema: Schema, part: str) -> Dict[str, Any]:
    """Get schema definition."""
    try:
        version_schema = SCHEMAS[schema]
    except KeyError:
        raise ValueError(f"Unknown schema {schema}")

    try:
        return version_schema[part]
    except KeyError:
        raise ValueError(f"Unknown schema part {schema}.{part}")
