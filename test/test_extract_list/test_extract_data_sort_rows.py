#! /usr/local/bin/python3
"""Test sorting of rows in extracted data for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import pytest
from extract_list.extract_config import ExtractConfig
from extract_list.extract_data import RowCompare, compare_values, sort_rows
from extract_list.commontypes import Data, Row, Value
from .check_capsys import check_capsys


@pytest.mark.parametrize('left,right,cols,res',
                         [({'a': 4, 'b': 5}, {'a': 3, 'b': 6},
                           ['b', 'a'], -1),
                          ({'a': 4, 'b': 5}, {'a': 3, 'b': 6},
                           ['a', 'b'], 1),
                          ({'a': 4, 'b': 5}, {'a': '3', 'b': '16'},
                           ['b', 'a'], 1),
                          ({'a': 4, 'b': 5}, {'a': '3', 'b': '16'},
                           ['a', 'b'], 1),
                          ({'a': 4, 'b': None}, {'a': None, 'b': 6},
                           ['b', 'a'], -1),
                          ({'a': 4, 'b': None}, {'a': None, 'b': 6},
                           ['a', 'b'], 1),
                          ({'a': None, 'b': 7}, {'a': None, 'b': 6},
                           ['a', 'b'], 1)])
def test_row_compare(capsys: pytest.CaptureFixture[str], left: Row, right: Row,
                     cols: list[str], res: int) -> None:
    """Test RowCompare."""
    cmp = RowCompare(cols=cols)
    ret = cmp.compare(left_row=left, right_row=right)
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('left,right,cols,res',
                         [({'a': None, 'b': None},
                           {'a': None, 'b': None}, ['a', 'b'], 0),
                          ({'a': 4, 'b': 5},
                           {'a': 4, 'b': 5}, ['a', 'b'], 0),
                          ({'a': '3'}, {'a': '4'}, ['a'], -1),
                          ({'a': datetime(2026, 1, 1)},
                           {'a': datetime(2026, 1, 2)}, ['a'], -1),
                          ({'a': timedelta(hours=1), 'b': 2},
                           {'a': timedelta(hours=1), 'b': 1}, ['a', 'b'], 1),
                          ({'a': timedelta(seconds=3), 'b': 'x'},
                           {'a': 3, 'b': 'x'}, ['a', 'b'], 0)])
def test_row_compare_ties(capsys: pytest.CaptureFixture[str], left: Row,
                          right: Row, cols: list[str], res: int) -> None:
    """Test row comparison ties and string-like comparisons."""
    cmp = RowCompare(cols=cols)
    ret = cmp.compare(left_row=left, right_row=right)
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ind,cols,outd',
                         [([{'a': 5, 'b': 7},
                            {'a': 3, 'b': 6},
                            {'a': 6, 'b': 6}], ['b', 'a'],
                           [{'a': 3, 'b': 6},
                            {'a': 6, 'b': 6},
                            {'a': 5, 'b': 7}]),
                          ([{'a': 5, 'b': 7, 'c': 8},
                            {'a': 3, 'b': 6, 'c': 5},
                            {'a': 6, 'b': 6, 'c': 0},
                            {'a': 6, 'b': 6, 'c': 1}],
                           ['b', 'a', 'c'],
                           [{'a': 3, 'b': 6, 'c': 5},
                            {'a': 6, 'b': 6, 'c': 0},
                            {'a': 6, 'b': 6, 'c': 1},
                            {'a': 5, 'b': 7, 'c': 8}]),
                          ([{'a': timedelta(hours=10), 'b': 2},
                            {'a': None, 'b': 9},
                            {'a': 3600, 'b': 1},
                            {'a': timedelta(hours=1), 'b': 0},
                            {'a': timedelta(hours=9), 'b': 3}],
                           ['a', 'b'],
                           [{'a': None, 'b': 9},
                            {'a': timedelta(hours=1), 'b': 0},
                            {'a': 3600, 'b': 1},
                            {'a': timedelta(hours=9), 'b': 3},
                            {'a': timedelta(hours=10), 'b': 2}])])
def test_sort_rows(capsys: pytest.CaptureFixture[str], ind: Data,
                   cols: list[str], outd: Data) -> None:
    """Test sort_rows."""
    cfg = ExtractConfig()
    cfg.order_rows_by = deepcopy(cols)
    ret = sort_rows(data=deepcopy(ind), cfg=cfg)
    assert ret == outd
    check_capsys(capsys=capsys)


UTC_PLUS_2 = timezone(timedelta(hours=2))


@pytest.mark.parametrize('left, right, res', [
    (None, None, 0), (None, 0, -1), (None, '', -1),
    (None, timedelta(0), -1),
    (timedelta(hours=1), timedelta(hours=1), 0),
    (timedelta(hours=9), timedelta(hours=10), -1),
    (timedelta(seconds=5), 5, 0), (timedelta(seconds=5), 4.5, 1),
    (3, timedelta(seconds=4), -1), (True, timedelta(seconds=1), 0),
    (timedelta(hours=10), '9:00:00', -1),
    (timedelta(hours=1), datetime(2026, 1, 1), -1),
    (datetime(2026, 1, 1), datetime(2026, 1, 1), 0),
    (datetime(2026, 1, 1, 9), datetime(2026, 1, 1, 10), -1),
    (datetime(2026, 1, 1, 12, tzinfo=UTC_PLUS_2),
     datetime(2026, 1, 1, 11, tzinfo=timezone.utc), -1),
    (datetime(2026, 1, 1, 12, tzinfo=UTC_PLUS_2),
     datetime(2026, 1, 1, 10, tzinfo=timezone.utc), 0),
    (datetime(2026, 1, 1, 12),
     datetime(2026, 1, 1, 11, tzinfo=timezone.utc), 1),
    (datetime(2026, 1, 2), '2026-01-01', 1),
    (1, 1.0, 0), (True, 1, 0), (2, 10.5, -1), (-1.5, -2, 1),
    (10, '9', -1), ('b', 'a', 1), ('', '', 0)])
def test_compare_values(capsys: pytest.CaptureFixture[str], left: Value,
                        right: Value, res: int) -> None:
    """Test compare_values, and that swapping the values negates the result.

    Values of the same kind compare by value, so timedelta(hours=10) is
    above timedelta(hours=9), and aware datetimes compare by the time they
    stand for, whatever the time zone. A truly mixed pair, such as a
    timedelta and a str, or a naive and an aware datetime, compares as str.
    """
    assert compare_values(left, right) == res
    assert compare_values(left=right, right=left) == -res
    check_capsys(capsys=capsys)
