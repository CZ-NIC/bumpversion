"""Settings for bumpversion.

Configuration can be defined on CLI or in one of the configuration files.
Currently supported locations are `.bumpversion.toml` and `pyproject.toml`
(searched in that order). The first found is used.

Arguments defined on CLI have a precedence over definition in configuration file.
"""
import os
from typing import Any, Dict, List, Optional, Tuple, cast

import tomli
from pydantic import (
    BaseModel,
    BaseSettings,
    Extra,
    Field,
    FilePath,
    PrivateAttr,
    root_validator,
    validator,
)
from pydantic.env_settings import SettingsSourceCallable
from pydantic.fields import ModelField

from .constants import Verbosity
from .schemas import Schema, get_schema

CONFIG_FILES = {
    ".bumpversion.toml": ["bumpversion"],
    "pyproject.toml": ["tool", "bumpversion"],
}


def _config_file_settings(settings: "Settings") -> Dict[str, Any]:
    config_file = settings._config_file
    sections = ["bumpversion"]
    if config_file is None:
        for _config_file, _sections in CONFIG_FILES.items():
            if os.path.isfile(_config_file):
                sections = _sections
                config_file = _config_file
                break
    if config_file:
        with open(config_file) as file:
            content = tomli.loads(file.read())
            for section in sections:
                content = content.get(section, {})
            content.setdefault("file", [])
            content["file"].append({"path": config_file})
            return content
    return {}


class Component(BaseModel):
    """Definition of a component in schema.

    Required key `cls` - a dotted path to a callable.

    All other keys are and passed as kwargs to the cls.
    """

    cls: str

    class Config:
        extra = Extra.allow


class File(BaseModel):
    """Definition of maintained file.

    Required key `path` - a relative path to a maintaned file on a filesystem.

    File specific `serializer` and `replacer` can be defined here as well.
    """

    path: FilePath
    serializer: Component
    replacer: Component

    class Config:
        extra = Extra.allow


class Settings(BaseSettings):
    """Settings class."""

    _config_file: Optional[str] = PrivateAttr(None)
    _verbosity: Verbosity = PrivateAttr(Verbosity.INFO)

    dry_run: bool = False
    """Whether actual replacements are performered."""
    allow_dirty: bool = False
    """Whether to proceed with bumping even though the VCS directory is not in a clean state."""
    commit: bool = False
    """Whether to create a commit in VCS."""
    commit_message: str = "Bump version: {current_version} → {new_version}"
    """
    The commit message that will be used when creating a commit.

    The message can use `current_version` and `new_version` placeholders.
    """
    commit_args: List[str] = []
    """Extra arguments to commit command.

    This is for example useful to add `-s` to generate `Signed-off-by:` line in the commit message.
    """
    tag: bool = False
    """Whether to create a tag in VCS. Tag is created by prefixing the new version with `v`."""
    tag_name: str = "v{new_version}"
    """
    The name of the tag that will be created.

    The message can use `current_version` and `new_version` placeholders.
    """
    tag_message: str = "Bump version: {current_version} → {new_version}"
    """
    The tag message that will be used when creating a tag.

    The message can use `current_version` and `new_version` placeholders.
    """
    sign_tags: bool = False
    """Whether to sign tags."""
    current_version: str = "0.0.0"
    """Current version in a string representation. It will be passed through `parser`."""
    version_schema: Optional[Schema] = Field(default=Schema.semver, alias="schema", env="schema")
    """
    What versioning schema to use.

    Currently supported are:

    * `semver`: Semantic Versioning
    * `pep440`: PEP440 compatible versioning

    Defines default settings for `bumper`, `parser`, `serializer` and `replacer`.
    """
    bumper: Component = Field(default=None)  # type: ignore[assignment]
    """
    Dotted path to a class that performs the actual bump of the `old version` to the `new version`.
    """
    parser: Component = Field(default=None)  # type: ignore[assignment]
    """Dotted path to a class that parses the `old version` to a dictionary representation."""
    serializer: Component = Field(default=None)  # type: ignore[assignment]
    """
    Dotted path to a class that serializes `new version` from its dictionary representation
    to a string.
    """
    replacer: Component = Field(default=None)  # type: ignore[assignment]
    """
    Dotted path to a class that perform the replacing of the `old version` by a `new version`.
    """
    file: List[File] = []
    """Definition for maintained files."""

    class Config:
        extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Include custom settings locations."""
            return (
                init_settings,
                env_settings,
                cast(SettingsSourceCallable, _config_file_settings),
                file_secret_settings,
            )

    def __init__(self, *args: Any, config_file: Optional[str] = None, **kwargs: Any):
        self._config_file = config_file
        super().__init__(*args, **kwargs)

    @root_validator
    def schema_definiton(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check that either schema is defined or all necessary components are defined."""
        if values.get("version_schema") is not None:
            # Schema is defined, we are going to use that
            return values
        parser = values.get("parser")
        serializer = values.get("serializer")
        replacer = values.get("replacer")
        if parser is not None and serializer is not None and replacer is not None:
            # We have all parts defined separatelly
            return values
        if parser is not None:
            # We have root level parser and bumper...
            # Lets have a look if we have parser/serializer in files
            for file in values.get("file", []):
                if file.serializer is None and serializer is None:
                    raise ValueError(f"{file.path} setting is missing serializer option")
                if file.replacer is None and replacer is None:
                    raise ValueError(f"{file.path} setting is missing replacer option")
            return values
        raise ValueError("Incomplete schema definition settings")

    @validator("file", each_item=True, pre=True)
    def fill_files(cls, v: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Pass root level settings to each individual file if not defined."""
        serializer = values.get("serializer")
        replacer = values.get("replacer")
        if v.get("serializer") is None:
            v["serializer"] = serializer
        if v.get("replacer") is None:
            v["replacer"] = replacer
        return v

    @validator("bumper", "parser", "serializer", "replacer", pre=True)
    def fill_schema(
        cls, v: Optional[Dict[str, Any]], field: ModelField, values: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Parse schema to individual settings.

        If schema is used, fill the root level settings for
        `bumper`, `parser`, `serializer` and `replacer` based on the schema if
        they are not defined on a root level as well.
        """
        if v is None and values.get("version_schema") is not None:
            v = get_schema(cast(Schema, values.get("version_schema")), field.name)
        return v
