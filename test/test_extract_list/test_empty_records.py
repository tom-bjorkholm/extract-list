#! /usr/local/bin/python3
"""Test input with empty records and empty path steps.

xmltodict gives None for an empty XML element, such as <l/>, and JSON can
hold null in the same places. An empty record holds no data and is skipped.
A path through an empty element has no value, so missing_input_for_column
decides what happens, except for the paths that link a linked line, which
must always have a value.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import pytest
import xmltodict
from config_as_json import JsonType
from extract_list.commontypes import Data, Value
from extract_list.config_enums import MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import LinkedLineSpec, MainLineSpec
from extract_list.extract_data import extract_data, get_at_path, get_lines
from .check_capsys import check_capsys

MISSING = [MissingInputForColumn.EMPTY, MissingInputForColumn.ERROR]
REC_A: JsonType = {'k': 'a', 'v': 'LA'}
REC_B: JsonType = {'k': 'b', 'v': 'LB'}


@pytest.mark.parametrize('indata, path', [
    (None, ['a']), ({'a': None}, ['a', 'b']),
    ({'a': {'b': None}}, ['a', 'b', 'c'])])
def test_path_through_empty(capsys: pytest.CaptureFixture[str],
                            indata: JsonType, path: list[str]) -> None:
    """Test that a path through None has no value with EMPTY."""
    assert get_at_path(indata=indata, path=path,
                       missing=MissingInputForColumn.EMPTY) is None
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('indata, path, key', [
    (None, ['a'], 'a'), ({'a': None}, ['a', 'b'], 'b'),
    ({'a': {'b': None}}, ['a', 'b', 'c'], 'c')])
def test_empty_path_error(capsys: pytest.CaptureFixture[str], indata: JsonType,
                          path: list[str], key: str) -> None:
    """Test that a path through None is a missing key with ERROR."""
    with pytest.raises(SystemExit):
        get_at_path(indata=indata, path=path,
                    missing=MissingInputForColumn.ERROR)
    check_capsys(capsys=capsys, in_err=f'No such key "{key}"')


@pytest.mark.parametrize('at_line, is_record, expand_at, expected', [
    ([None, REC_A, None, REC_B], False, [], [(1, REC_A), (3, REC_B)]),
    ([None, REC_A], True, [], [(1, REC_A)]),
    ([None, None], False, [], []),
    ({'x': None, 'y': REC_A}, False, [], [('y', REC_A)]),
    ({'x': None}, True, [], [(0, {'x': None})]),
    ([], False, [], []), ({}, False, [], []),
    (None, False, [], [(0, None)]), (None, True, [], [(0, None)]),
    ([{'k': 'a', 'n': [None, REC_B]}], False, [['n']],
     [(0, {'k': 'a', 'n': None}), (0, {'k': 'a', 'n': REC_B})])])
def test_get_lines_empty(capsys: pytest.CaptureFixture[str], at_line: JsonType,
                         is_record: bool, expand_at: list[list[str]],
                         expected: list[tuple[Value, JsonType]]) -> None:
    """Test that get_lines skips empty records, keeping the other keys.

    Only None at "line" itself means no value there, which gives (0, None).
    An empty element in a list at an expand_at path is not a record, so it
    still gives a line, where paths through it have no value.
    """
    spec = MainLineSpec(data={'line': ['top'], 'columns': {},
                              'expand_at': expand_at,
                              'dict_at_line_is_record': is_record})
    result = list(get_lines(indata={'top': at_line},
                            missing=MissingInputForColumn.ERROR, spec=spec))
    assert result == expected
    check_capsys(capsys=capsys)


def xml_config(missing: MissingInputForColumn,
               include_key: bool = False) -> ExtractConfig:
    """Return config for main records <m> linked by <k> to records <l>.

    A single <m> or <l> is one record (dict_at_line_is_record).
    """
    cfg = ExtractConfig()
    cfg.missing_input_for_column = missing
    cfg.main_line = MainLineSpec(data={
        'line': ['d', 'm'], 'columns': {'X': ['x'], 'S': ['a', 's']},
        'expand_at': [], 'dict_at_line_is_record': True})
    cfg.linked_lines = [LinkedLineSpec(data={
        'line': ['d', 'l'], 'columns': {'V': ['v']}, 'linked_column': ['k'],
        'linked_main_column': ['k'], 'expand_at': [],
        'dict_at_line_is_record': True})]
    cfg.one_output_line_per_main_line = True
    cfg.include_key = include_key
    cfg.column_order = []
    return cfg


def extract_xml(xml: str, cfg: ExtractConfig) -> Data:
    """Return the data extracted from the XML text."""
    indata: JsonType = xmltodict.parse(xml)
    return extract_data(indata=indata, cfg=cfg)


M1 = '<m><x>1</x><k>a</k><a><s>s1</s></a></m>'
M2 = '<m><x>2</x><k>b</k><a><s>s2</s></a></m>'
L1 = '<l><k>a</k><v>LA</v></l>'
L2 = '<l><k>b</k><v>LB</v></l>'
ROW1 = {'X': '1', 'S': 's1', 'V': 'LA'}
ROW2 = {'X': '2', 'S': 's2', 'V': 'LB'}


@pytest.mark.parametrize('missing', MISSING)
@pytest.mark.parametrize('xml, expected', [
    (f'<d>{M1}{M2}<l/>{L1}{L2}</d>', [ROW1, ROW2]),
    (f'<d>{M1}{M2}{L1}<l/>{L2}</d>', [ROW1, ROW2]),
    (f'<d><m/>{M1}<m/>{M2}{L1}{L2}</d>', [ROW1, ROW2]),
    ('<d><m/><m/><l/></d>', [])])
def test_skip_empty_records(capsys: pytest.CaptureFixture[str],
                            missing: MissingInputForColumn, xml: str,
                            expected: Data) -> None:
    """Test that empty elements among the records are skipped.

    The records after an empty element must still be read, for main lines
    as well as for linked lines.
    """
    assert extract_xml(xml, xml_config(missing)) == expected
    check_capsys(capsys=capsys)


def test_skip_keeps_keys(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the key column keeps the index of each record."""
    xml = f'<d><m/>{M1}<m/>{M2}{L1}{L2}</d>'
    cfg = xml_config(MissingInputForColumn.ERROR, include_key=True)
    key = cfg.column_name_for_key
    assert extract_xml(xml, cfg) == [ROW1 | {key: 1}, ROW2 | {key: 3}]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('xml, expected', [
    (f'<d><m><x>1</x><k>a</k><a/></m>{L1}</d>', [ROW1 | {'S': None}]),
    (f'<d><m><x/><k>a</k><a><s/></a></m>{L1}</d>',
     [ROW1 | {'X': None, 'S': None}]),
    (f'<d>{M1}<l/></d>', [ROW1 | {'V': None}]),
    (f'<d>{M1}<l/><l/></d>', [ROW1 | {'V': None}]),
    (f'<d>{M1}<l><k>a</k><v/></l></d>', [ROW1 | {'V': None}]),
    (f'<d>{M1}<l><k/><v>LA</v></l></d>', [ROW1 | {'V': None}])])
def test_empty_values(capsys: pytest.CaptureFixture[str], xml: str,
                      expected: Data) -> None:
    """Test that empty elements give empty cells with EMPTY.

    An empty link key is the value None, which matches no main record.
    """
    cfg = xml_config(MissingInputForColumn.EMPTY)
    assert extract_xml(xml, cfg) == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('xml, msg', [
    (f'<d><m><x>1</x><k>a</k><a/></m>{L1}</d>', 'No such key "s"'),
    (f'<d>{M1}<l/></d>', 'No linked line has'),
    (f'<d>{M1}<l/><l/></d>', 'No linked line has'),
    (f'<d>{M1}<l><k/><v>LA</v></l></d>', 'No linked line has')])
def test_empty_values_err(capsys: pytest.CaptureFixture[str], xml: str,
                          msg: str) -> None:
    """Test that empty elements where values are needed stop with ERROR."""
    with pytest.raises(SystemExit):
        extract_xml(xml, xml_config(MissingInputForColumn.ERROR))
    check_capsys(capsys=capsys, in_err=msg)


@pytest.mark.parametrize('missing', MISSING)
@pytest.mark.parametrize('xml', [f'<d>{M1}<l><v>LA</v></l></d>',
                                 f'<d><m><x>1</x><a><s>1</s></a></m>{L1}</d>'])
def test_link_key_needed(capsys: pytest.CaptureFixture[str],
                         missing: MissingInputForColumn, xml: str) -> None:
    """Test that a record without its link key stops the extraction.

    The link key is not a column, so this holds whatever
    missing_input_for_column says.
    """
    with pytest.raises(SystemExit):
        extract_xml(xml, xml_config(missing))
    check_capsys(capsys=capsys, in_err='No such key "k"')
