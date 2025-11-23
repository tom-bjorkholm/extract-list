#! /usr/local/bin/python3
"""Define types that are common for several files."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional
from datetime import datetime
from enum import Enum, auto

type Value = Optional[str | int | bool | float | datetime]
type Row = dict[str, Value]
type Data = list[Row]


class CfgTypes(Enum):
    """Types of example configurations."""

    SW_JSON_TO_RRS = auto()
    SW_XML_TO_RRS = auto()
    EXAMPLE_JSON = auto()
    EXAMPLE_XML = auto()
    EXAMPLE2_JSON = auto()
    EXAMPLE2_XML = auto()
