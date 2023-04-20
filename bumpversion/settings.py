"""Settings module for bumpversion."""
import os
from typing import Any, Dict, List, Optional, Tuple, cast

import tomli
from pydantic import BaseModel, BaseSettings, Extra, Field, FilePath, PrivateAttr
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


class Schema(BaseModel):
    """Definition of versioning schema."""

    parser: Component
    bumper: Component
    serializer: Component
    replacer: Component


class File(BaseModel):
    """Definition of maintained file."""

    path: FilePath
    version_schema: Optional[str] = Field(default=None, alias="schema")

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
    version_schema: Dict[str, Schema] = Field(default_factory=dict, alias="schema")
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
