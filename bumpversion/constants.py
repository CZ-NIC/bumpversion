"""Constants."""
from enum import IntEnum, unique


@unique
class Verbosity(IntEnum):
    """Verbosity levels."""

    SILENT = 0
    INFO = 1
    DETAIL = 2
    DEBUG = 3
