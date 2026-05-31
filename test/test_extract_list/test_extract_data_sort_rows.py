#! /usr/local/bin/python3
"""Test sorting of rows in extracted data for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
import pytest
from extract_list.extract_config import ExtractConfig
from extract_list.extract_data import RowCompare, sort_rows
from extract_list.commontypes import Data, Row
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
                            {'a': 5, 'b': 7, 'c': 8}])])
def test_sort_rows(capsys: pytest.CaptureFixture[str], ind: Data,
                   cols: list[str], outd: Data) -> None:
    """Test sort_rows."""
    cfg = ExtractConfig()
    cfg.order_rows_by = deepcopy(cols)
    ret = sort_rows(data=deepcopy(ind), cfg=cfg)
    assert ret == outd
    check_capsys(capsys=capsys)
