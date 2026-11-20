#! /usr/local/bin/python3
"""Test expanding records at expand_at paths when extracting data."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from copy import deepcopy
import pytest
from config_as_json import JsonType
from extract_list.config_enums import MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import LinkedLineSpec, MainLineSpec
from extract_list.extract_data import expand_line, get_lines, extract_data
from extract_list.commontypes import Data, Value
from .check_capsys import check_capsys

ITEM_A: JsonType = {'i': 'a', 'parts': [1, 2]}
ITEM_B: JsonType = {'i': 'b', 'parts': [3]}
REC_LIST: JsonType = {'n': 1, 'items': [ITEM_A, ITEM_B], 'tags': ['x', 'y']}
REC_ONE: JsonType = {'n': 2, 'items': ITEM_A, 'tags': ['x', 'y']}
REC_EMPTY: JsonType = {'n': 3, 'items': [], 'tags': ['x']}


@pytest.mark.parametrize('rec,expand,expected', [
    (REC_LIST, [], [REC_LIST]),
    (REC_LIST, [['missing']], [REC_LIST]),
    (REC_ONE, [['items', 'missing']], [REC_ONE]),
    (REC_ONE, [['items']], [REC_ONE]),
    (REC_EMPTY, [['items']], []),
    (REC_LIST, [['items']],
     [{'n': 1, 'items': ITEM_A, 'tags': ['x', 'y']},
      {'n': 1, 'items': ITEM_B, 'tags': ['x', 'y']}]),
    (REC_LIST, [['items'], ['items', 'parts']],
     [{'n': 1, 'items': {'i': 'a', 'parts': 1}, 'tags': ['x', 'y']},
      {'n': 1, 'items': {'i': 'a', 'parts': 2}, 'tags': ['x', 'y']},
      {'n': 1, 'items': {'i': 'b', 'parts': 3}, 'tags': ['x', 'y']}]),
    (REC_LIST, [['items'], ['tags']],
     [{'n': 1, 'items': ITEM_A, 'tags': 'x'},
      {'n': 1, 'items': ITEM_A, 'tags': 'y'},
      {'n': 1, 'items': ITEM_B, 'tags': 'x'},
      {'n': 1, 'items': ITEM_B, 'tags': 'y'}]),
    (REC_ONE, [['items'], ['tags']],
     [{'n': 2, 'items': ITEM_A, 'tags': 'x'},
      {'n': 2, 'items': ITEM_A, 'tags': 'y'}])])
def test_expand_line(capsys: pytest.CaptureFixture[str], rec: JsonType,
                     expand: list[list[str]],
                     expected: list[JsonType]) -> None:
    """Test that expand_line gives one new line per list element.

    Collecting all lines before comparing also checks that the lines do not
    share data, and the record given must be left unchanged.
    """
    original = deepcopy(rec)
    result = list(expand_line(skey='k', dline=rec, expand=expand))
    assert result == [('k', line) for line in expected]
    assert rec == original
    check_capsys(capsys=capsys)


EXPANDED: list[JsonType] = [
    {'n': 1, 'items': ITEM_A, 'tags': ['x', 'y']},
    {'n': 1, 'items': ITEM_B, 'tags': ['x', 'y']}, REC_ONE]


@pytest.mark.parametrize('records,keys', [
    ([REC_LIST, REC_ONE, REC_EMPTY], [0, 0, 1]),
    ({'r1': REC_LIST, 'r2': REC_ONE, 'r3': REC_EMPTY}, ['r1', 'r1', 'r2'])])
def test_get_lines_expand(capsys: pytest.CaptureFixture[str],
                          records: JsonType, keys: list[Value]) -> None:
    """Test that get_lines expands records held in a list or in a dict."""
    indata: JsonType = {'top': {'recs': records}}
    original = deepcopy(indata)
    result = list(get_lines(indata=indata, missing=MissingInputForColumn.ERROR,
                            path=['top', 'recs'], expand_at=[['items']]))
    assert result == list(zip(keys, EXPANDED))
    assert indata == original
    check_capsys(capsys=capsys)


ORDERS: JsonType = [
    {'customer': '66', 'items': [{'item': 'apple', 'quantity': '5'},
                                 {'item': 'carrot', 'quantity': '2'}]},
    {'customer': '22', 'items': {'item': 'banana', 'quantity': '1'}},
    {'customer': '66', 'items': []}]
CUSTOMERS: JsonType = [{'name': 'Donald', 'number': '66'},
                       {'name': 'Mickey', 'number': '22'}]
INDATA: JsonType = {'data': {'orders': ORDERS, 'customers': CUSTOMERS}}
ITEM_COLUMNS = {'What': ['items', 'item'], 'How many': ['items', 'quantity']}


def config_orders_main() -> ExtractConfig:
    """Return config with the orders, expanded at items, as main line."""
    cfg = ExtractConfig()
    cfg.main_line = MainLineSpec(data={
        'line': ['data', 'orders'], 'expand_at': [['items']],
        'columns': {'Customer': ['customer']} | ITEM_COLUMNS})
    cfg.linked_lines = []
    cfg.column_order = ['Customer', 'What', 'How many']
    return cfg


def config_orders_linked() -> ExtractConfig:
    """Return config with the orders, expanded at items, as linked line."""
    cfg = ExtractConfig()
    cfg.main_line = MainLineSpec(data={
        'line': ['data', 'customers'], 'expand_at': [],
        'columns': {'Customer': ['name']}})
    cfg.linked_lines = [LinkedLineSpec(data={
        'line': ['data', 'orders'], 'expand_at': [['items']],
        'columns': ITEM_COLUMNS, 'linked_column': ['customer'],
        'linked_main_column': ['number']})]
    cfg.one_output_line_per_main_line = False
    cfg.column_order = ['Customer', 'What', 'How many']
    return cfg


@pytest.mark.parametrize('cfg,expected', [
    (config_orders_main(),
     [{'Customer': '22', 'What': 'banana', 'How many': '1'},
      {'Customer': '66', 'What': 'apple', 'How many': '5'},
      {'Customer': '66', 'What': 'carrot', 'How many': '2'}]),
    (config_orders_linked(),
     [{'Customer': 'Donald', 'What': 'apple', 'How many': '5'},
      {'Customer': 'Donald', 'What': 'carrot', 'How many': '2'},
      {'Customer': 'Mickey', 'What': 'banana', 'How many': '1'}])])
def test_extract_data_expand(capsys: pytest.CaptureFixture[str],
                             cfg: ExtractConfig, expected: Data) -> None:
    """Test extract_data expanding records held in lists, as from XML."""
    cfg.include_key = False
    cfg.missing_input_for_column = MissingInputForColumn.ERROR
    assert extract_data(indata=deepcopy(INDATA), cfg=cfg) == expected
    check_capsys(capsys=capsys)
