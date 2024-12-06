#! /usr/local/bin/python3
"""Functions for actual extractions of list of columns from JSON or XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import Optional, Tuple, Generator, cast
import sys
# from copy import deepcopy
from excel_list_transform.commontypes import JsonType
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import MissingInputForColumn
from extract_list.commontypes import Data, Row, Value


class MainDataLine:  # pylint: disable=too-few-public-methods
    """Data of main line."""

    def __init__(self, complete_line: JsonType, key: str | int, row: Row):
        """Construct MainData with data of main line."""
        self.complete_line: JsonType = complete_line
        self.key: str | int = key
        self.row: Row = row


class PathNotInData(KeyError):
    """Exception for path not in in indata."""


def get_at_path(indata: JsonType, path: list[str],
                missing: MissingInputForColumn) -> Optional[JsonType]:
    """Get the data at path in JSON indata."""
    assert len(path) >= 1
    pkey = path[0]
    if not isinstance(indata, dict):
        print('Input data does not match configuration.',
              file=sys.stderr)
        print(f'Trying to extract data at {path} in data that is ' +
              f'{type(indata).__name__} and not dict.',
              file=sys.stderr)
        sys.exit(1)
    assert isinstance(indata, dict)
    if pkey not in indata:
        if missing == MissingInputForColumn.ERROR:
            print(f'No such key "{pkey}" in relevant section in input data.',
                  file=sys.stderr)
            sys.exit(1)
        else:
            return None
    if len(path) > 1:
        return get_at_path(indata[pkey], path[1:], missing=missing)
    return indata[pkey]


def get_lines(indata: JsonType, missing: MissingInputForColumn,
              path: list[str]) -> Generator[Tuple[Value, JsonType],
                                            None, None]:
    """Get (as generator) all items in indata under path."""
    lines: JsonType = get_at_path(indata=indata, path=path, missing=missing)
    if lines is None:
        yield (0, None)
        return
    assert lines is not None
    if not isinstance(lines, (list, dict)):
        yield (0, lines)  # single value at path
        return
    assert isinstance(lines, (list, dict))
    if isinstance(lines, list):
        assert isinstance(lines, list)
        llines: list[JsonType] = cast(list[JsonType], lines)
        for key, dat in enumerate(llines):
            yield (key, dat)
    elif isinstance(lines, dict):
        assert isinstance(lines, dict)
        dlines: dict[str | int, JsonType] = \
            cast(dict[str | int, JsonType], lines)
        for skey, ddat in dlines.items():
            if not isinstance(skey, (int, str)):
                print(f'Key "{skey}" is not str or int as expected',
                      file=sys.stderr)
                sys.exit(1)
            assert isinstance(skey, (int, str))
            ddat = dlines[skey]
            yield (skey, ddat)
    else:  # pragma: no cover
        print('internal error in get_line()', file=sys.stderr)
        print(f'lines is {type(lines).__name__}', file=sys.stderr)
        sys.exit(1)


def get_columns(inline: JsonType, colspec: dict[str, list[str]],
                missing: MissingInputForColumn) -> Row:
    """Map data in input line to columns."""
    ret: Row = {}
    for colname, path in colspec.items():
        assert isinstance(path, list)
        val = get_at_path(indata=inline, path=path, missing=missing)
        if isinstance(val, (list, dict)):
            print(f'Expected a single value for {colname} at {path}\n',
                  f'but found data of type {type(val).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        assert not isinstance(val, (list, dict))
        ret[colname] = val
    return ret


def extract_main_line(indata: JsonType,
                      cfg: ExtractConfig) -> Generator[MainDataLine,
                                                       None, None]:
    """Extract columns with values according to main_line spec."""
    for key, line in get_lines(indata=indata,
                               missing=cfg.missing_input_for_column,
                               path=cfg.main_line.line):
        if line is None:
            print('No data matching main line in input', file=sys.stderr)
            print(f'Main line path is {cfg.main_line.line}',
                  file=sys.stderr)
            sys.exit(1)
        assert line is not None
        if not isinstance(key, (int, str)):  # pragma no cover
            print(f'Key "{key}" is not str or int as expected',
                  file=sys.stderr)
            sys.exit(1)
        assert isinstance(key, (int, str))
        row = get_columns(inline=line, colspec=cfg.main_line.columns,
                          missing=cfg.missing_input_for_column)
        if cfg.include_key:
            row[cfg.column_name_for_key] = key
        yield MainDataLine(complete_line=line, key=key,
                           row=row)


def extract_data(indata: JsonType, cfg: ExtractConfig) -> Data:
    """Extract columns (with values) from input data."""
    data: Data = []
    for row in extract_main_line(indata=indata, cfg=cfg):
        data.append(row.row)
    if cfg.linked_lines:
        print('Sorry, extracting of linked lines not yet implemented,',
              file=sys.stderr)
    return data
