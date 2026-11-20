#! /usr/local/bin/python3
"""Functions for actual extractions of list of columns from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, Tuple, Generator, Iterable, Sequence
import sys
from copy import deepcopy
from datetime import datetime, timedelta
from functools import cmp_to_key
from config_as_json import JsonType
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import LineSpecBase, \
    LinkedLineSpec
from extract_list.config_enums import MissingInputForColumn
from extract_list.commontypes import Data, Row, Value


class MainDataLine:  # pylint: disable=too-few-public-methods
    """Data of main line."""

    def __init__(self, complete_line: JsonType, key: str | int,
                 row: Row) -> None:
        """Construct MainData with data of main line."""
        self.complete_line: JsonType = complete_line
        self.key: str | int = key
        self.row: Row = row


class PathNotInData(KeyError):
    """Exception for path not in in indata."""


def get_at_path(indata: JsonType, path: list[str],
                missing: MissingInputForColumn) -> Optional[JsonType]:
    """Get the data at path in JSON indata.

    None, such as an empty XML element, has no keys, so a path through it
    is handled like a missing key, as given by missing.
    """
    assert len(path) >= 1
    pkey = path[0]
    if indata is None:
        indata = {}
    if not isinstance(indata, dict):
        print('Input data does not match configuration.', file=sys.stderr)
        print(f'Trying to extract data at {path} in data that is ' +
              f'{type(indata).__name__} and not dict.',
              file=sys.stderr)
        print(f'indata={indata}', file=sys.stderr)
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


def set_at_path(data: JsonType, path: Sequence[str | int],
                newdata: JsonType) -> None:
    """Set newdata at path in data, modifying data."""
    assert isinstance(path, list)
    assert isinstance(data, (list, dict))
    assert len(path) > 0
    if len(path) > 1:
        set_at_path(data=data[path[0]], path=path[1:], newdata=newdata)
    else:
        data[path[0]] = newdata


def expand_line(skey: Value, dline: JsonType,
                expand: list[list[str]]) -> Generator[Tuple[Value, JsonType],
                                                      None, None]:
    """Expand json line to one line per element of the lists at expand.

    Each path in expand is applied in order. A list at a path gives one
    line per element, with the element in place of the list, so an empty
    list gives no line at all. Any other value at a path, such as a single
    XML element, or no value, leaves the line as it is. Every line yielded
    is a new object, and dline is never modified.
    """
    if not expand:
        yield (skey, dline)
        return
    path, rest = expand[0], expand[1:]
    atpath = get_at_path(indata=dline, path=path,
                         missing=MissingInputForColumn.EMPTY)
    if not isinstance(atpath, list):
        yield from expand_line(skey=skey, dline=dline, expand=rest)
        return
    for elem in atpath:
        line = deepcopy(dline)
        set_at_path(data=line, path=path, newdata=deepcopy(elem))
        yield from expand_line(skey=skey, dline=line, expand=rest)


def keyed_records(lines: list[JsonType] | dict[str, JsonType],
                  dict_is_record: bool) \
        -> Iterable[Tuple[str | int, JsonType]]:
    """Return the records with their list index or dict key.

    With dict_is_record true, a dict is not records keyed by name but a
    single record, such as an XML element that occurs only once. It is
    then returned like a list of that one record, with index 0.
    """
    if isinstance(lines, list):
        return enumerate(lines)
    if dict_is_record:
        return enumerate([lines])
    for key in lines:
        if not isinstance(key, (int, str)):
            print(f'Key "{key}" is not str or int as expected',
                  file=sys.stderr)
            sys.exit(1)
    return lines.items()


def get_lines(indata: JsonType, missing: MissingInputForColumn,
              spec: LineSpecBase) -> Generator[Tuple[Value, JsonType],
                                               None, None]:
    """Get (as generator) all items in indata under spec.line.

    The items may be held in a list or in a dict, and each item is
    expanded at the paths in spec.expand_at (see expand_line). With
    spec.dict_at_line_is_record true, a dict under spec.line is one item
    (see keyed_records). An item that is None, such as an empty XML
    element, holds no record and is skipped. When there is no value at
    spec.line, the only item yielded is (0, None).
    """
    lines: JsonType = get_at_path(indata=indata, path=spec.line,
                                  missing=missing)
    if lines is None:
        yield (0, None)
        return
    if not isinstance(lines, (list, dict)):
        yield (0, lines)  # single value at path
        return
    for key, record in keyed_records(lines, spec.dict_at_line_is_record):
        if record is not None:
            yield from expand_line(skey=key, dline=record,
                                   expand=spec.expand_at)


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
                               spec=cfg.main_line):
        if line is None:
            print('No data matching main line in input', file=sys.stderr)
            print(f'Main line path is {cfg.main_line.line}', file=sys.stderr)
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
        yield MainDataLine(complete_line=line, key=key, row=row)


def create_none_columns(colspec: dict[str, list[str]]) -> Row:
    """Create a row with columns and None values."""
    ret: Row = {key: None for key in colspec.keys()}
    return ret


def extract_linked_line(indata: JsonType, main_line: MainDataLine,
                        cfg: ExtractConfig,
                        linked_spec: LinkedLineSpec) -> Data:
    """Extract columns (with values) for linked lines from input data."""
    if not linked_spec.columns:
        return [{}]
    ret: Data = []
    main_match_value = get_at_path(indata=main_line.complete_line,
                                   path=linked_spec.linked_main_column,
                                   missing=MissingInputForColumn.ERROR)
    for _, line in get_lines(indata=indata,
                             missing=cfg.missing_input_for_column,
                             spec=linked_spec):
        if line is None:
            break
        assert line is not None
        link_match_val = get_at_path(indata=line,
                                     path=linked_spec.linked_column,
                                     missing=MissingInputForColumn.ERROR)
        if link_match_val == main_match_value:
            row = get_columns(inline=line, colspec=linked_spec.columns,
                              missing=cfg.missing_input_for_column)
            ret.append(row)
    if not ret:
        if cfg.missing_input_for_column == MissingInputForColumn.ERROR:
            print('Input data not consistent with configuration.',
                  file=sys.stderr)
            print(f'No linked line has {linked_spec.linked_column} ' +
                  f' with value {main_match_value}', file=sys.stderr)
            sys.exit(1)
        else:
            ret.append(create_none_columns(colspec=linked_spec.columns))
    return ret


def add_from_linked_to_main(from_main: Data, from_linked: Data) -> Data:
    """Add lines from linked to lines from main."""
    assert len(from_linked) > 0
    assert len(from_main) > 0
    if len(from_linked) == 1:
        for row in from_main:
            row.update(from_linked[0])
        return from_main
    ret: Data = []
    for linkline in from_linked:
        mainline = deepcopy(from_main)
        for row in mainline:
            row.update(deepcopy(linkline))
        ret.extend(mainline)
    return ret


def _sign[T: (str, float, datetime, timedelta)](left: T, right: T) -> int:
    """Return -1, 0 or 1 as left is less than, equal to or above right."""
    return int(left > right) - int(left < right)


def _as_timedelta(value: Value, other: Value) -> Value:
    """Return value as seconds when compared to a timedelta (other)."""
    if isinstance(other, timedelta) and isinstance(value, (int, float)):
        return timedelta(seconds=value)
    return value


def _same_awareness(left: datetime, right: datetime) -> bool:
    """Return True if both datetimes are naive or both are aware."""
    return (left.utcoffset() is None) == (right.utcoffset() is None)


def compare_values(left: Value, right: Value) -> int:
    """Compare two values, returning -1, 0 or 1 as for sorting.

    None comes before any other value. Numbers compare by value with
    numbers, and with a timedelta as that many seconds. Two timedeltas, or
    two datetimes that are both naive or both aware, compare by value. Any
    other mix of types, such as a str and a number, compares as the str of
    each value.
    """
    if left is None or right is None:
        return int(left is not None) - int(right is not None)
    left, right = _as_timedelta(left, right), _as_timedelta(right, left)
    if isinstance(left, timedelta) and isinstance(right, timedelta):
        return _sign(left, right)
    if isinstance(left, datetime) and isinstance(right, datetime) and \
            _same_awareness(left, right):
        return _sign(left, right)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return _sign(left, right)
    return _sign(str(left), str(right))


class RowCompare:  # pylint: disable=too-few-public-methods
    """Function object class to compare rows for sorting."""

    def __init__(self, cols: list[str]) -> None:
        """Construct object that will be used to compare rows."""
        self.cols: list[str] = cols

    def compare(self, left_row: Row, right_row: Row) -> int:
        """Compare two Rows by the values in cols (see compare_values).

        The first column in cols where the values differ decides.
        """
        for col in self.cols:
            result = compare_values(left_row[col], right_row[col])
            if result != 0:
                return result
        return 0


def sort_rows(data: Data, cfg: ExtractConfig) -> Data:
    """Sort the rows in data as configured."""
    cmp = RowCompare(cfg.get_order_rows_by())
    return sorted(data, key=cmp_to_key(cmp.compare))


def extract_data(indata: JsonType, cfg: ExtractConfig) -> Data:
    """Extract columns (with values) from input data."""
    data: Data = []
    for row in extract_main_line(indata=indata, cfg=cfg):
        data_for_row: Data = [row.row]
        for linked_spec in cfg.linked_lines:
            linkdata = extract_linked_line(indata=indata, main_line=row,
                                           cfg=cfg, linked_spec=linked_spec)
            assert len(linkdata) > 0
            if len(linkdata) > 1:
                if cfg.one_output_line_per_main_line:
                    print('Several linked lines match one main line, ' +
                          'but configuration says one line per main line',
                          file=sys.stderr)
                    sys.exit(1)
            data_for_row = add_from_linked_to_main(from_main=data_for_row,
                                                   from_linked=linkdata)
        data.extend(data_for_row)
    return sort_rows(data=data, cfg=cfg)
