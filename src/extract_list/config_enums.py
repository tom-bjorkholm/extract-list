#! /usr/local/bin/python3
"""Enumerations used in configuration."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from enum import Enum, auto
from itertools import chain
from excel_list_transform.config_enums import FileType as ExcFileType


class TxtFileType(Enum):
    """Output file type."""

    TXT = len(ExcFileType) + 1


OutOnlyFileType = Enum('OutOnlyFileType',
                       [(i.name, i.value) for i in
                        chain(ExcFileType, TxtFileType)])


class InFileType(Enum):
    """Input file type."""

    JSON = len(OutOnlyFileType) + 1
    XML = auto()


OutFileType = Enum('OutFileType',
                   [(i.name, i.value) for i in
                    chain(OutOnlyFileType, InFileType)])
