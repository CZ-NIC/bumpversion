"""Settings module for bumpversion."""
import os
from typing import Any, Dict, List, Optional, Tuple, cast

import tomli
from pydantic import BaseModel, BaseSettings, Extra, Field, FilePath
from pydantic.env_settings import SettingsSourceCallable

CONFIG_FILES = {
    "bumpversion.toml": False,
    "pyproject.toml": True,
}


def _config_file_settings(settings: "Settings") -> Dict[str, Any]:
    for name in CONFIG_FILES.keys():
        full_name = os.path.expanduser(name)
        if os.path.isfile(full_name):
            config_file = full_name
            pyproject_file = CONFIG_FILES[name]
            break
    if config_file:
        with open(config_file) as file:
            content = tomli.loads(file.read())
            if pyproject_file:
                content = content.get("tool", {})
            return cast(Dict[str, Any], content.get("bumpversion", {}))
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

    commit: bool = False
    tag: bool = False
    allow_dirty: str = ""
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
