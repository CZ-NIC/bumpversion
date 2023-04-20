"""Settings module for bumpversion."""
import os
from typing import Any, Dict, List, Optional, Tuple, cast

import tomli
from pydantic import BaseModel, BaseSettings, Extra, Field, FilePath, PrivateAttr, root_validator
from pydantic.env_settings import SettingsSourceCallable

from .constants import Verbosity

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
    serializer: Optional[Component] = None
    replacer: Optional[Component] = None

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
    version_schema: Optional[str] = Field(default=None, alias="schema")
    bumper: Optional[Component] = None
    parser: Optional[Component] = None
    serializer: Optional[Component] = None
    replacer: Optional[Component] = None
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
        bumper = values.get("bumper")
        parser = values.get("parser")
        serializer = values.get("serializer")
        replacer = values.get("replacer")
        if (
            bumper is not None
            and parser is not None
            and serializer is not None
            and replacer is not None
        ):
            # We have all parts defined separatelly
            return values
        if bumper is not None and parser is not None:
            # We have root level parser and bumper...
            # Lets have a look if we have parser/serializer in files
            for file in values.get("file", []):
                if file.serializer is None and serializer is None:
                    raise ValueError(f"{file.path} setting is missing serializer option")
                if file.replacer is None and replacer is None:
                    raise ValueError(f"{file.path} setting is missing replacer option")
            return values
        raise ValueError("Incomplete schema definition settings")
