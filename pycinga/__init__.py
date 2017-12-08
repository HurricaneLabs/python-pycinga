"""
This package provides all the modules for writing an Icinga plugin
with Python. The package file itself exports the constants used
throughout the library.
"""

import argparse  # NOQA

from .plugin import Plugin, OK, WARNING, CRITICAL, UNKNOWN  # NOQA
from .range import Range  # NOQA
from .response import Response  # NOQA
from .status import Status  # NOQA

version = "1.0.0"
"""Current version of Pycinga"""
