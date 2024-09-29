#! /usr/local/bin/python3
"""Define types that are common for several files."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import Optional, TypeAlias
from datetime import datetime

Value: TypeAlias = Optional[str | int | bool | float | datetime]
Row: TypeAlias = dict[str, Value]
Data: TypeAlias = list[Row]
