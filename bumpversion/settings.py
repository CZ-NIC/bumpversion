"""Settings module for bumpversion."""
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
    "bumpversion.toml": ["bumpversion"],
    "pyproject.toml": ["tool", "bumpversion"],
}


def _config_file_settings(settings: "Settings") -> Dict[str, Any]:
    config_file = settings._config_file
    sections = ["bumpversion"]
    if config_file is None:
        for config_file, _sections in CONFIG_FILES.items():
            if os.path.isfile(config_file):
                sections = _sections
                break
    if config_file:
        with open(config_file) as file:
            content = tomli.loads(file.read())
            for section in sections:
                content = content.get(section, {})
            content["file"].append({"path": config_file})
            return content
    return {}


class Component(BaseModel):
    """Definition of a component in schema.

    cls: Dotted path to a callble
    extra items are parsed and passed as kwargs to the cls
    """

    cls: str

    class Config:
        extra = Extra.allow


class File(BaseModel):
    """Definition of maintained file."""

    path: FilePath
    serializer: Component
    replacer: Component

    class Config:
        extra = Extra.allow


class Settings(BaseSettings):
    """Settings."""

    _config_file: Optional[str] = PrivateAttr(None)
    _verbosity: Verbosity = PrivateAttr(Verbosity.INFO)

    dry_run: bool = False
    commit: bool = False
    tag: bool = False
    allow_dirty: bool = False
    current_version: Optional[str] = None
    version_schema: Optional[Schema] = Field(default=None, alias="schema", env="schema")
    bumper: Component = Field(default=None)  # type: ignore[assignment]
    parser: Component = Field(default=None)  # type: ignore[assignment]
    serializer: Component = Field(default=None)  # type: ignore[assignment]
    replacer: Component = Field(default=None)  # type: ignore[assignment]
    file: List[File] = []

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
        """Check that we either have a schema or all necessary parts."""
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
        """Make sure that all files have all settings."""
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
        """Fill values if schema is used."""
        if v is None and values.get("version_schema") is not None:
            v = get_schema(cast(Schema, values.get("version_schema")), field.name)
        return v
