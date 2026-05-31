#! /usr/local/bin/python3
"""Enumerations and output format list helpers used in configuration."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from enum import Enum, auto
from typing import Optional
from tableio import CAP_IGNORABLE, CAP_NEEDED, CAP_NOT_USED, Capabilities, \
    list_implementations_tableio, list_registered_tableio
from tableio.capability import SingleCapability


INTERNAL_OUTFILE_FORMATS = ['JSON', 'XML']


class InFileType(Enum):
    """Input file type."""  # Code duplication due to mypy limitation

    JSON = auto()
    XML = auto()


class FormatRequest(Enum):
    """Request level for optional output format features."""

    NO = auto()
    IF_AVAILABLE = auto()
    NEEDED = auto()


def _single_capability_from_request(
        format_request: FormatRequest) -> SingleCapability:
    """Get single capability from format request."""
    if format_request == FormatRequest.NO:
        return CAP_NOT_USED
    if format_request == FormatRequest.IF_AVAILABLE:
        return CAP_IGNORABLE
    return CAP_NEEDED


def get_outfile_capabilities(border: FormatRequest = FormatRequest.NO,
                             filtered_area: FormatRequest
                             = FormatRequest.NO) -> Capabilities:
    """Get capabilities based on border and filtered area."""
    fcap = _single_capability_from_request(filtered_area)
    bcap = _single_capability_from_request(border)
    return Capabilities(can_write=CAP_NEEDED, can_read=CAP_NOT_USED,
                        can_fmt_row=CAP_NOT_USED, can_fmt_value=CAP_NOT_USED,
                        filtered_data_range=fcap, can_write_box=CAP_NOT_USED,
                        can_read_box=CAP_NOT_USED,
                        can_write_highlight=CAP_NOT_USED,
                        multi_sheet=CAP_NOT_USED,
                        can_find_value_position=CAP_NOT_USED,
                        can_write_borders=bcap)


def _internal_formats(border: FormatRequest,
                      filtered_area: FormatRequest) -> list[str]:
    """Get internal output formats compatible with requested features."""
    if FormatRequest.NEEDED in (border, filtered_area):
        return []
    return INTERNAL_OUTFILE_FORMATS.copy()


def list_out_file_formats(border: FormatRequest = FormatRequest.NO,
                          filtered_area: FormatRequest
                          = FormatRequest.NO) -> list[str]:
    """List available output file types."""
    cap = get_outfile_capabilities(border, filtered_area)
    formats = list_registered_tableio(capabilities=cap, empty_is_ok=True)
    formats.extend(_internal_formats(border, filtered_area))
    return formats


def is_internal_out_file_format(format_name: str) -> bool:
    """Return True if the output format is handled inside extract-list."""
    return format_name.lower() in [x.lower() for x in INTERNAL_OUTFILE_FORMATS]


def list_out_format_implementations(format_name: Optional[str] = None,
                                    border: FormatRequest = FormatRequest.NO,
                                    filtered_area: FormatRequest
                                    = FormatRequest.NO) -> list[str]:
    """List available output format implementations."""
    if format_name is not None and is_internal_out_file_format(format_name):
        return ['internal']
    cap = get_outfile_capabilities(border, filtered_area)
    ret = list_implementations_tableio(format_name=format_name,
                                       capabilities=cap, empty_is_ok=True)
    if format_name is None:
        ret.append('internal')
    return ret


class MissingInputForColumn(Enum):
    """What to do if path for column does not exist."""

    ERROR = auto()
    EMPTY = auto()
