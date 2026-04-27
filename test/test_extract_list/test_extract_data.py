#! /usr/local/bin/python3
"""Test extracting of data for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
from typing import Optional, cast
import pytest
from excel_list_transform.commontypes import JsonType
from extract_list.config_enums import MissingInputForColumn
from extract_list.extract_config import ExtractConfig, LinkedLineSpec, \
    MainLineSpec
from extract_list.extract_data import get_at_path, \
    get_lines, get_columns, extract_main_line, MainDataLine, \
    extract_data, create_none_columns, add_from_linked_to_main, \
    extract_linked_line
from extract_list.commontypes import Data, Row
from .check_capsys import check_capsys


da1: dict[str, JsonType] = {'ab': 'c', 'de': 'g', 'fg': 9}
da2: dict[str, JsonType] = {'ax': 'h', 'bx': 'ij', 'cx': 7}
db1: dict[str, JsonType] = {'xq': da1, 'xw': 'kl', 'xe': da2}
db2: dict[str, JsonType] = {
    'yq': {'mn': 6, 'op': da2}, 'yw': 4, 'ye': {'za': 2, 'zb': da2}}
dc1: dict[str, JsonType] = {'qa': 3, 'qb': db1, 'qc': 'rst', 'qd': db2}


@pytest.mark.parametrize('mis',
                         [MissingInputForColumn.EMPTY,
                          MissingInputForColumn.ERROR])
@pytest.mark.parametrize('ind,pat,res',
                         [(da1, ['de'], 'g'),
                          (db1, ['xe', 'bx'], 'ij'),
                          (db2, ['yq', 'op'], da2),
                          (dc1, ['qb', 'xq', 'fg'], 9)])
def test_get_at_path_ok1(capsys: pytest.CaptureFixture[str],
                         mis: MissingInputForColumn, ind: JsonType,
                         pat: list[str], res: JsonType) -> None:
    """Test OK cases 1 of get_at_path."""
    ret = get_at_path(indata=deepcopy(ind), path=pat, missing=mis)
    check_capsys(capsys=capsys)
    assert ret == res


@pytest.mark.parametrize('ind,pat,res',
                         [(da1, ['dq'], None),
                          (db1, ['xe', 'bxx'], None),
                          (db2, ['yq', 'op', 'ff'], None),
                          (dc1, ['qb', 'xq', 'fg'], 9)])
def test_get_at_path_ok2(capsys: pytest.CaptureFixture[str],
                         ind: JsonType, pat: list[str],
                         res: JsonType) -> None:
    """Test OK cases 2 of get_at_path."""
    ret = get_at_path(indata=deepcopy(ind), path=pat,
                      missing=MissingInputForColumn.EMPTY)
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('mis',
                         [MissingInputForColumn.EMPTY,
                          MissingInputForColumn.ERROR])
@pytest.mark.parametrize('ind,pat,msgs',
                         [(da1, ['de', 'ab'],
                           ['Input data does not match configuration.',
                            "Trying to extract data at ['ab'] in data that is",
                            'str and not dict']),
                          (db1, ['xe', 'bx', 'ax'],
                           ['Input data does not match configuration.',
                            "Trying to extract data at ['ax'] in data that is",
                            'str and not dict']),
                          (db2, ['yq', 'op', 'cx', 'ab'],
                           ['Input data does not match configuration.',
                            "Trying to extract data at ['ab'] in data that is",
                            'int and not dict']),
                          (dc1, ['qb', 'xq', 'fg', 'ax'],
                           ['Input data does not match configuration.',
                            "Trying to extract data at ['ax'] in data that is",
                            'int and not dict'])])
def test_get_at_path_nok1(capsys: pytest.CaptureFixture[str],
                          mis: MissingInputForColumn, ind: JsonType,
                          pat: list[str], msgs: list[str]) -> None:
    """Test OK cases 1 of get_at_path."""
    with pytest.raises(SystemExit):
        _ = get_at_path(indata=deepcopy(ind), path=pat, missing=mis)
    check_capsys(capsys=capsys, in_err=msgs)


@pytest.mark.parametrize('ind,pat,msgs',
                         [(da1, ['dq'],
                           ['No such key "dq" in relevant section in',
                            'in input data.']),
                          (db1, ['xe', 'bxx'],
                           ['No such key "bxx" in relevant section in',
                            'in input data.']),
                          (db2, ['yq', 'op', 'ff'],
                           ['No such key "ff" in relevant section in',
                            'in input data.']),
                          (dc1, ['qb', 'xq', 'fg1'],
                           ['No such key "fg1" in relevant section in',
                            'in input data.'])])
def test_get_at_path_nok2(capsys: pytest.CaptureFixture[str],
                          ind: JsonType, pat: list[str],
                          msgs: list[str]) -> None:
    """Test OK cases 1 of get_at_path."""
    with pytest.raises(SystemExit):
        _ = get_at_path(indata=deepcopy(ind), path=pat,
                        missing=MissingInputForColumn.ERROR)
    check_capsys(capsys=capsys, in_err=msgs)


dd1: dict[str, JsonType] = {'a': 'bc', 'b': 'de', 'c': 4}
dd2: dict[str, JsonType] = {'a': 'fg', 'b': 'hi', 'c': 5}
dd3: dict[str, JsonType] = {'a': 'jk', 'b': 'lm', 'c': 6}
dd4: dict[str, JsonType] = {'a': 'no', 'b': 'pq', 'c': 7}
de1: dict[str, JsonType] = {'d': 'abc', 'e': 'def', 'f': 4}
de2: dict[str, JsonType] = {'d': 'ghi', 'e': 'jkl', 'f': 5}
de3: dict[str, JsonType] = {'d': 'mno', 'e': 'pqr', 'f': 6}
de4: dict[str, JsonType] = {'d': 'stu', 'e': 'vwx', 'f': 6}
de5: dict[str, JsonType] = {'d': 'yza', 'e': 'bcd', 'f': 7}
de6: dict[str, JsonType] = {'d': 'efg', 'e': 'hij', 'f': 7}
dda: list[JsonType] = [dd1, dd2, dd3, dd4]
dea: list[JsonType] = [de1, de2, de3, de4, de5, de6]
ddm: dict[str, JsonType] = {'d1': dd1, 'd2': dd2, 'd3': dd3, 'd4': dd4}
dem: dict[str, JsonType] = {
    'e1': de1, 'e2': de2, 'e3': de3, 'e4': de4, 'e5': de5, 'e6': de6}
dfa: dict[str, JsonType] = {'g': {'h': dda}, 'k': dea}
dfm: dict[str, JsonType] = {'g': {'h': ddm}, 'k': dem}


@pytest.mark.parametrize('mis', [MissingInputForColumn.EMPTY,
                                 MissingInputForColumn.ERROR])
@pytest.mark.parametrize('inp,pat,res',
                         [(dfa, ['g', 'h'], dda),
                          (dfa, ['k'], dea),
                          (dfm, ['g', 'h'], dda),
                          (dfm, ['k'], dea),
                          (dfm, ['k', 'e1', 'f'], [4])])
def test_get_lines_ok1(capsys: pytest.CaptureFixture[str],
                       mis: MissingInputForColumn, inp: JsonType,
                       pat: list[str], res: list[JsonType]) -> None:
    """Test OK cases 1 for get_lines."""
    result = deepcopy(res)
    counter = 0
    for index, (_, line) in enumerate(get_lines(indata=deepcopy(inp),
                                                missing=mis, path=pat,
                                                expand_at=[])):
        assert line == result[index]
        counter += 1
    assert len(result) == counter
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('inp,pat',
                         [(dfa, ['g', 'k']),
                          (dfa, ['m']),
                          (dfm, ['g', 'h', 'x']),
                          (dfm, ['k', 'e47']),
                          (dfm, ['k', 'e1', 'g'])])
def test_get_lines_ok2(capsys: pytest.CaptureFixture[str],
                       inp: JsonType, pat: list[str]) -> None:
    """Test OK cases 2 for get_lines."""
    counter = 0
    for index, (_, line) in \
        enumerate(get_lines(indata=deepcopy(inp),
                            missing=MissingInputForColumn.EMPTY,
                            path=pat, expand_at=[])):
        assert line is None
        counter += 1
        assert 0 == index
    assert 1 == counter
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('inp,pat',
                         [(dfa, ['g', 'k']),
                          (dfa, ['m']),
                          (dfm, ['g', 'h', 'x']),
                          (dfm, ['k', 'e47']),
                          (dfm, ['k', 'e1', 'g'])])
def test_get_lines_nok1(capsys: pytest.CaptureFixture[str],
                        inp: JsonType, pat: list[str]) -> None:
    """Test not OK cases 1 for get_lines."""
    counter = 0
    with pytest.raises(SystemExit):
        for index, (_, line) in \
            enumerate(get_lines(indata=deepcopy(inp),
                                missing=MissingInputForColumn.ERROR,
                                path=pat, expand_at=[])):
            assert line is None
            counter += 1
            assert 0 == index
    assert 0 == counter
    errmsgs = ['No such key ', ' in relevant section']
    check_capsys(capsys=capsys, in_err=errmsgs)


@pytest.mark.parametrize('inp, pat',
                         [({'a':
                            {MissingInputForColumn.EMPTY: {'b': 1, 'c': 2},
                             MissingInputForColumn.ERROR: {'b': 4, 'c': 5}}},
                           ['a'])])
def test_get_lines_nok2(capsys: pytest.CaptureFixture[str], inp: object,
                        pat: list[str]) -> None:
    """Test not OK cases 2 for get_lines."""
    counter = 0
    with pytest.raises(SystemExit):
        for index, (_, line) in \
            enumerate(get_lines(indata=cast(JsonType, deepcopy(inp)),
                                missing=MissingInputForColumn.EMPTY,
                                path=pat, expand_at=[])):
            assert line is None
            counter += 1
            assert 0 == index
    assert 0 == counter
    errmsgs = ['Key "MissingInputForColumn.EMPTY" is not str',
               ' is not str or int as expected']
    check_capsys(capsys=capsys, in_err=errmsgs)


@pytest.mark.parametrize('mis', [MissingInputForColumn.EMPTY,
                                 MissingInputForColumn.ERROR])
@pytest.mark.parametrize('inp,spec,res',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['a']},
                           {'x': 'de', 'y': 4, 'z': 'bc'}),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'c']},
                           {'c1': 'de', 'c2': 5})])
def test_get_columns_ok1(capsys: pytest.CaptureFixture[str],
                         mis: MissingInputForColumn, inp: JsonType,
                         spec: dict[str, list[str]], res: Row) -> None:
    """Test OK cases 1 of get_columns."""
    ret = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                      missing=mis)
    assert res == ret
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('inp,spec,res',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['d']},
                           {'x': 'de', 'y': 4, 'z': None}),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'cc']},
                           {'c1': 'de', 'c2': None})])
def test_get_columns_ok2(capsys: pytest.CaptureFixture[str],
                         inp: JsonType, spec: dict[str, list[str]],
                         res: Row) -> None:
    """Test OK cases 2 of get_columns."""
    ret = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                      missing=MissingInputForColumn.EMPTY)
    assert res == ret
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('inp,spec,msg',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['d']},
                           'No such key "d"'),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'cc']},
                           'No such key "cc"')])
def test_get_columns_nok1(capsys: pytest.CaptureFixture[str],
                          inp: JsonType, spec: dict[str, list[str]],
                          msg: str) -> None:
    """Test not OK cases 1 of get_columns."""
    with pytest.raises(SystemExit):
        _ = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                        missing=MissingInputForColumn.ERROR)
    errmsgs = [msg, '" in relevant section in input data.']
    check_capsys(capsys=capsys, in_err=errmsgs)


@pytest.mark.parametrize('inp,spec,msg',
                         [(dfa, {'x': ['g', 'h'], 'y': 'k'},
                           "Expected a single value for x at ['g', 'h']"),
                          (ddm, {'c1': ['d1'], 'c2': ['d3']},
                           "Expected a single value for c1 at ['d1']")])
def test_get_columns_nok2(capsys: pytest.CaptureFixture[str],
                          inp: JsonType, spec: dict[str, list[str]],
                          msg: str) -> None:
    """Test not OK cases 2 of get_columns."""
    with pytest.raises(SystemExit):
        _ = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                        missing=MissingInputForColumn.ERROR)
    errmsgs = [msg, 'but found data of type']
    check_capsys(capsys=capsys, in_err=errmsgs)


ta1 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, False, '',
       [{'complete_line': dd1, 'key': 0,
         'row': {'c1': 'de', 'c2': 4, 'c3': 'bc'}},
        {'complete_line': dd2, 'key': 1,
         'row': {'c1': 'hi', 'c2': 5, 'c3': 'fg'}},
        {'complete_line': dd3, 'key': 2,
         'row': {'c1': 'lm', 'c2': 6, 'c3': 'jk'}},
        {'complete_line': dd4, 'key': 3,
         'row': {'c1': 'pq', 'c2': 7, 'c3': 'no'}}])
ta2 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.ERROR, False, '',
       [{'complete_line': dd1, 'key': 0,
         'row': {'c1': 'de', 'c2': 4, 'c3': 'bc'}},
        {'complete_line': dd2, 'key': 1,
         'row': {'c1': 'hi', 'c2': 5, 'c3': 'fg'}},
        {'complete_line': dd3, 'key': 2,
         'row': {'c1': 'lm', 'c2': 6, 'c3': 'jk'}},
        {'complete_line': dd4, 'key': 3,
         'row': {'c1': 'pq', 'c2': 7, 'c3': 'no'}}])
ta3 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, False, '',
       [{'complete_line': dd1, 'key': 0,
         'row': {'c1': 'de', 'c2': 4, 'c3': None}},
        {'complete_line': dd2, 'key': 1,
         'row': {'c1': 'hi', 'c2': 5, 'c3': None}},
        {'complete_line': dd3, 'key': 2,
         'row': {'c1': 'lm', 'c2': 6, 'c3': None}},
        {'complete_line': dd4, 'key': 3,
         'row': {'c1': 'pq', 'c2': 7, 'c3': None}}])
ta4 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, False, '',
       [{'complete_line': dd1, 'key': 'd1',
         'row': {'c1': 'de', 'c2': 4, 'c3': 'bc'}},
        {'complete_line': dd2, 'key': 'd2',
         'row': {'c1': 'hi', 'c2': 5, 'c3': 'fg'}},
        {'complete_line': dd3, 'key': 'd3',
         'row': {'c1': 'lm', 'c2': 6, 'c3': 'jk'}},
        {'complete_line': dd4, 'key': 'd4',
         'row': {'c1': 'pq', 'c2': 7, 'c3': 'no'}}])
ta5 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.ERROR, False, '',
       [{'complete_line': dd1, 'key': 'd1',
         'row': {'c1': 'de', 'c2': 4, 'c3': 'bc'}},
        {'complete_line': dd2, 'key': 'd2',
         'row': {'c1': 'hi', 'c2': 5, 'c3': 'fg'}},
        {'complete_line': dd3, 'key': 'd3',
         'row': {'c1': 'lm', 'c2': 6, 'c3': 'jk'}},
        {'complete_line': dd4, 'key': 'd4',
         'row': {'c1': 'pq', 'c2': 7, 'c3': 'no'}}])
ta6 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, False, '',
       [{'complete_line': dd1, 'key': 'd1',
         'row': {'c1': 'de', 'c2': 4, 'c3': None}},
        {'complete_line': dd2, 'key': 'd2',
         'row': {'c1': 'hi', 'c2': 5, 'c3': None}},
        {'complete_line': dd3, 'key': 'd3',
         'row': {'c1': 'lm', 'c2': 6, 'c3': None}},
        {'complete_line': dd4, 'key': 'd4',
         'row': {'c1': 'pq', 'c2': 7, 'c3': None}}])
ta7 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, True, 'col_key',
       [{'complete_line': dd1, 'key': 0,
         'row': {'c1': 'de', 'c2': 4, 'c3': 'bc', 'col_key': 0}},
        {'complete_line': dd2, 'key': 1,
         'row': {'c1': 'hi', 'c2': 5, 'c3': 'fg', 'col_key': 1}},
        {'complete_line': dd3, 'key': 2,
         'row': {'c1': 'lm', 'c2': 6, 'c3': 'jk', 'col_key': 2}},
        {'complete_line': dd4, 'key': 3,
         'row': {'c1': 'pq', 'c2': 7, 'c3': 'no', 'col_key': 3}}])
ta8 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, True, 'xyz',
       [{'complete_line': dd1, 'key': 'd1',
         'row': {'c1': 'de', 'c2': 4, 'c3': None, 'xyz': 'd1'}},
        {'complete_line': dd2, 'key': 'd2',
         'row': {'c1': 'hi', 'c2': 5, 'c3': None, 'xyz': 'd2'}},
        {'complete_line': dd3, 'key': 'd3',
         'row': {'c1': 'lm', 'c2': 6, 'c3': None, 'xyz': 'd3'}},
        {'complete_line': dd4, 'key': 'd4',
         'row': {'c1': 'pq', 'c2': 7, 'c3': None, 'xyz': 'd4'}}])


@pytest.mark.parametrize('tax',
                         [ta1, ta2, ta2, ta3, ta4, ta5, ta6, ta7, ta8])
def test_extract_main_line_ok1(capsys: pytest.CaptureFixture[str],
                               tax: tuple[object, ...]) -> None:
    """Test OK cases 1 of extract_main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = cast(MissingInputForColumn, tax[3])
    cfg.main_line.line = cast(list[str], tax[1])
    cfg.main_line.columns = cast(dict[str, list[str]], tax[2])
    cfg.main_line.expand_at = []
    cfg.include_key = cast(bool, tax[4])
    cfg.column_name_for_key = cast(str, tax[5])
    expected_rows = cast(list[dict[str, JsonType]], tax[6])
    indata = cast(JsonType, tax[0])
    for ret, expected in zip(extract_main_line(indata=indata, cfg=cfg),
                             expected_rows):
        exp_main = MainDataLine(
            complete_line=expected['complete_line'],
            key=cast(str | int, expected['key']),
            row=cast(Row, expected['row']))
        assert ret.complete_line == exp_main.complete_line
        assert ret.key == exp_main.key
        assert ret.row == exp_main.row
    num = 0
    for _ in extract_main_line(indata=indata, cfg=cfg):
        num += 1
    assert num == len(expected_rows)
    check_capsys(capsys=capsys)


tb1 = (dfm, ['g', 'k'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, True, 'xyz')
tb2 = ({'a':
        {MissingInputForColumn.EMPTY: {'b': 1, 'c': 2},
         MissingInputForColumn.ERROR: {'b': 4, 'c': 5}}},
       ['a'], {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, True, 'xyz')


@pytest.mark.parametrize('tbx,msgs',
                         [(tb1, ['No data matching main line in input',
                                 "Main line path is ['g', 'k']"]),
                          (tb2, ['Key "MissingInputForColumn.EMPTY" is not',
                                 'Y" is not str or int as expected'])])
def test_extract_main_line_nok1(capsys: pytest.CaptureFixture[str],
                                tbx: tuple[object, ...],
                                msgs: list[str]) -> None:
    """Test not OK cases 1 of extract_main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = cast(MissingInputForColumn, tbx[3])
    cfg.main_line.line = cast(list[str], tbx[1])
    cfg.main_line.columns = cast(dict[str, list[str]], tbx[2])
    cfg.include_key = cast(bool, tbx[4])
    cfg.column_name_for_key = cast(str, tbx[5])
    with pytest.raises(SystemExit):
        for _ in extract_main_line(indata=cast(JsonType, tbx[0]), cfg=cfg):
            pass
    check_capsys(capsys=capsys, in_err=msgs)


tc1 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': 'bc'},
        {'c1': 'hi', 'c2': 5, 'c3': 'fg'},
        {'c1': 'lm', 'c2': 6, 'c3': 'jk'},
        {'c1': 'pq', 'c2': 7, 'c3': 'no'}])
tc2 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.ERROR, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': 'bc'},
        {'c1': 'hi', 'c2': 5, 'c3': 'fg'},
        {'c1': 'lm', 'c2': 6, 'c3': 'jk'},
        {'c1': 'pq', 'c2': 7, 'c3': 'no'}])
tc3 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': None},
        {'c1': 'hi', 'c2': 5, 'c3': None},
        {'c1': 'lm', 'c2': 6, 'c3': None},
        {'c1': 'pq', 'c2': 7, 'c3': None}])
tc4 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': 'bc'},
        {'c1': 'hi', 'c2': 5, 'c3': 'fg'},
        {'c1': 'lm', 'c2': 6, 'c3': 'jk'},
        {'c1': 'pq', 'c2': 7, 'c3': 'no'}])
tc5 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.ERROR, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': 'bc'},
        {'c1': 'hi', 'c2': 5, 'c3': 'fg'},
        {'c1': 'lm', 'c2': 6, 'c3': 'jk'},
        {'c1': 'pq', 'c2': 7, 'c3': 'no'}])
tc6 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, False, '',
       [{'c1': 'de', 'c2': 4, 'c3': None},
        {'c1': 'hi', 'c2': 5, 'c3': None},
        {'c1': 'lm', 'c2': 6, 'c3': None},
        {'c1': 'pq', 'c2': 7, 'c3': None}])
tc7 = (dfa, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['a']},
       MissingInputForColumn.EMPTY, True, 'col_key',
       [{'c1': 'de', 'c2': 4, 'c3': 'bc', 'col_key': 0},
        {'c1': 'hi', 'c2': 5, 'c3': 'fg', 'col_key': 1},
        {'c1': 'lm', 'c2': 6, 'c3': 'jk', 'col_key': 2},
        {'c1': 'pq', 'c2': 7, 'c3': 'no', 'col_key': 3}])
tc8 = (dfm, ['g', 'h'],
       {'c1': ['b'], 'c2': ['c'], 'c3': ['abc']},
       MissingInputForColumn.EMPTY, True, 'xyz',
       [{'c1': 'de', 'c2': 4, 'c3': None, 'xyz': 'd1'},
        {'c1': 'hi', 'c2': 5, 'c3': None, 'xyz': 'd2'},
        {'c1': 'lm', 'c2': 6, 'c3': None, 'xyz': 'd3'},
        {'c1': 'pq', 'c2': 7, 'c3': None, 'xyz': 'd4'}])


@pytest.mark.parametrize('tcx',
                         [tc1, tc2, tc2, tc3, tc4, tc5, tc6, tc7, tc8])
def test_extract_data_mainline_ok1(capsys: pytest.CaptureFixture[str],
                                   tcx: tuple[object, ...]) -> None:
    """Test OK cases 1 of extract_data for main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = cast(MissingInputForColumn, tcx[3])
    cfg.main_line.line = cast(list[str], tcx[1])
    cfg.main_line.columns = cast(dict[str, list[str]], tcx[2])
    cfg.include_key = cast(bool, tcx[4])
    cfg.column_name_for_key = cast(str, tcx[5])
    cfg.linked_lines = []
    cfg.column_order = []
    res = extract_data(indata=cast(JsonType, deepcopy(tcx[0])), cfg=cfg)
    assert res == cast(Data, tcx[6])
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('spec,res',
                         [({}, {}),
                          ({'qwe': ['a', 'b'], 'asd': ['c']},
                           {'qwe': None, 'asd': None})])
def test_create_none_columns(capsys: pytest.CaptureFixture[str],
                             spec: dict[str, list[str]], res: Row) -> None:
    """Test create_none_columns."""
    ret = create_none_columns(colspec=deepcopy(spec))
    assert res == ret
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('fma,fli,res',
                         [([{}], [{}], [{}]),
                          ([{'a': 'b'}], [{'c': 'd'}],
                           [{'a': 'b', 'c': 'd'}]),
                          ([{'a': 'b'}, {'c': 2}],
                           [{'d': 'e'}],
                           [{'a': 'b', 'd': 'e'}, {'c': 2, 'd': 'e'}]),
                          ([{'a': 'b'}],
                           [{'d': 'e'}, {'f': 3}],
                           [{'a': 'b', 'd': 'e'}, {'a': 'b', 'f': 3}]),
                          ([{'a': 'b'}, {'c': 2}],
                           [{'d': 'e'}, {'f': 3}],
                           [{'a': 'b', 'd': 'e'}, {'a': 'b', 'f': 3},
                            {'c': 2, 'd': 'e'}, {'c': 2, 'f': 3}])])
def test_add_fr_linked_main_ok1(capsys: pytest.CaptureFixture[str],
                                fma: Data, fli: Data, res: Data) -> None:
    """Tesk OK cases 1 of add_from_linked_to_main."""
    ret = add_from_linked_to_main(from_main=deepcopy(fma),
                                  from_linked=deepcopy(fli))
    check_capsys(capsys=capsys)
    assert len(ret) == len(res)
    if len(res) == 0:
        return
    for item in ret:
        assert item in res
    if len(res) == 1 and res[0] == {}:
        assert ret[0] == {}
        return
    assert sorted(ret, key=lambda x: sorted(list(x.keys()))[0]) == \
        sorted(res, key=lambda x: sorted(list(x.keys()))[0])


columns: dict[str, list[str]] = {'C2': ['e'], 'C3': ['d']}


@pytest.mark.parametrize('ind,conf,res',
                         [(dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.EMPTY,
                            LinkedLineSpec({'line': ['k'], 'columns': columns,
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{'C2': 'def', 'C3': 'abc'}]),
                          (dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.EMPTY,
                            LinkedLineSpec({'line': ['k'], 'columns': columns,
                                            'linked_column': ['d'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{'C2': None, 'C3': None}]),
                          (dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.EMPTY,
                            LinkedLineSpec({'line': ['k2'], 'columns': columns,
                                            'linked_column': ['d'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{'C2': None, 'C3': None}]),
                          (dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.EMPTY,
                            LinkedLineSpec({'line': ['k'], 'columns': {},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{}]),
                          (dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'], 'columns': columns,
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{'C2': 'def', 'C3': 'abc'}]),
                          (dfa,
                           (MainDataLine(dd3, 0, {'C1': 'bc'}),
                            MissingInputForColumn.EMPTY,
                            LinkedLineSpec({'line': ['k'], 'columns': columns,
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           [{'C2': 'pqr', 'C3': 'mno'},
                            {'C2': 'vwx', 'C3': 'stu'}])])
def test_extr_linked_line_ok1(capsys: pytest.CaptureFixture[str],
                              ind: JsonType,
                              conf: tuple[MainDataLine,
                                          MissingInputForColumn,
                                          LinkedLineSpec],
                              res: Data) -> None:
    """Test OK cases 1 of extract_linked_line."""
    main_line: MainDataLine = conf[0]
    linked_spec: LinkedLineSpec = conf[2]
    cfg = ExtractConfig()
    cfg.missing_input_for_column = conf[1]
    cfg.linked_lines = [linked_spec]
    ret = extract_linked_line(indata=ind, main_line=main_line,
                              cfg=cfg, linked_spec=linked_spec)
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ind,conf,msgs',
                         [(dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'], 'columns': columns,
                                            'linked_column': ['d'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           ["No linked line has ['d']",
                            'with value 4',
                            'Input data not consistent with configuration.']),
                          (dfa,
                           (MainDataLine(dd1, 0, {'C1': 'bc'}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k2'], 'columns': columns,
                                            'linked_column': ['e'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []})),
                           ['No such key "k2" in relevant section',
                            'relevant section in input data'])])
def test_extr_linked_line_nok1(capsys: pytest.CaptureFixture[str],
                               ind: JsonType,
                               conf: tuple[MainDataLine,
                                           MissingInputForColumn,
                                           LinkedLineSpec],
                               msgs: list[str]) -> None:
    """Test not OK cases 1 of extract_linked_line."""
    main_line: MainDataLine = conf[0]
    linked_spec: LinkedLineSpec = conf[2]
    cfg = ExtractConfig()
    cfg.missing_input_for_column = conf[1]
    cfg.linked_lines = [linked_spec]
    with pytest.raises(SystemExit):
        _ = extract_linked_line(indata=ind, main_line=main_line,
                                cfg=cfg, linked_spec=linked_spec)
    check_capsys(capsys=capsys, in_err=msgs)


@pytest.mark.parametrize('ind,conf,res',
                         [(dfa,
                           (MainLineSpec(data={'line': ['k'],
                                               'columns': {'C1': ['d']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['g', 'h'],
                                            'columns': {'C2': ['b']},
                                            'linked_column': ['c'],
                                            'linked_main_column': ['f'],
                                            'expand_at': []}),
                            None, True, False),
                           [{'C1': 'abc', 'C2': 'de'},
                            {'C1': 'ghi', 'C2': 'hi'},
                            {'C1': 'mno', 'C2': 'lm'},
                            {'C1': 'stu', 'C2': 'lm'},
                            {'C1': 'yza', 'C2': 'pq'},
                            {'C1': 'efg', 'C2': 'pq'}]),
                          (dfa,
                           (MainLineSpec(data={'line': ['g', 'h'],
                                               'columns': {'C1': ['b']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C2': ['d']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            None, False, False),
                           [{'C1': 'de', 'C2': 'abc'},
                            {'C1': 'hi', 'C2': 'ghi'},
                            {'C1': 'lm', 'C2': 'mno'},
                            {'C1': 'lm', 'C2': 'stu'},
                            {'C1': 'pq', 'C2': 'yza'},
                            {'C1': 'pq', 'C2': 'efg'}]),
                          (dfa,
                           (MainLineSpec(data={'line': ['g', 'h'],
                                               'columns': {'C1': ['b']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C2': ['d']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C3': ['e']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            False, False),
                           [{'C1': 'de', 'C2': 'abc', 'C3': 'def'},
                            {'C1': 'hi', 'C2': 'ghi', 'C3': 'jkl'},
                            {'C1': 'lm', 'C2': 'mno', 'C3': 'pqr'},
                            {'C1': 'lm', 'C2': 'stu', 'C3': 'pqr'},
                            {'C1': 'lm', 'C2': 'mno', 'C3': 'vwx'},
                            {'C1': 'lm', 'C2': 'stu', 'C3': 'vwx'},
                            {'C1': 'pq', 'C2': 'yza', 'C3': 'bcd'},
                            {'C1': 'pq', 'C2': 'efg', 'C3': 'bcd'},
                            {'C1': 'pq', 'C2': 'yza', 'C3': 'hij'},
                            {'C1': 'pq', 'C2': 'efg', 'C3': 'hij'}]),
                          (dfa,
                           (MainLineSpec(data={'line': ['k'],
                                               'columns': {'C1': ['d']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['g', 'h'],
                                            'columns': {'C2': ['b']},
                                            'linked_column': ['c'],
                                            'linked_main_column': ['f'],
                                            'expand_at': []}),
                            None, True, True),
                           [{'C1': 'abc', 'key col': 0, 'C2': 'de'},
                            {'C1': 'ghi', 'key col': 1, 'C2': 'hi'},
                            {'C1': 'mno', 'key col': 2, 'C2': 'lm'},
                            {'C1': 'stu', 'key col': 3, 'C2': 'lm'},
                            {'C1': 'yza', 'key col': 4, 'C2': 'pq'},
                            {'C1': 'efg', 'key col': 5, 'C2': 'pq'}]),
                          (dfm,
                           (MainLineSpec(data={'line': ['k'],
                                               'columns': {'C1': ['d']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['g', 'h'],
                                            'columns': {'C2': ['b']},
                                            'linked_column': ['c'],
                                            'linked_main_column': ['f'],
                                            'expand_at': []}),
                            None, True, True),
                           [{'C1': 'abc', 'key col': 'e1', 'C2': 'de'},
                            {'C1': 'ghi', 'key col': 'e2', 'C2': 'hi'},
                            {'C1': 'mno', 'key col': 'e3', 'C2': 'lm'},
                            {'C1': 'stu', 'key col': 'e4', 'C2': 'lm'},
                            {'C1': 'yza', 'key col': 'e5', 'C2': 'pq'},
                            {'C1': 'efg', 'key col': 'e6', 'C2': 'pq'}])])
def test_extract_data_ok1(capsys: pytest.CaptureFixture[str], ind: JsonType,
                          conf: tuple[MainLineSpec, MissingInputForColumn,
                                      LinkedLineSpec,
                                      Optional[LinkedLineSpec], bool, bool],
                          res: Data) -> None:
    """Test OK cases 1 of extract_data."""
    main_line: MainLineSpec = conf[0]
    linked_spec: LinkedLineSpec = conf[2]
    linked_spec2: Optional[LinkedLineSpec] = conf[3]
    cfg = ExtractConfig()
    cfg.missing_input_for_column = conf[1]
    cfg.linked_lines = [linked_spec]
    if linked_spec2 is not None:
        cfg.linked_lines.append(linked_spec2)
    cfg.main_line = main_line
    cfg.one_output_line_per_main_line = conf[4]
    cfg.include_key = conf[5]
    cfg.column_order = []
    ret = extract_data(indata=ind, cfg=cfg)
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ind,conf,msgs',
                         [(dfa,
                           (MainLineSpec(data={'line': ['g', 'h'],
                                               'columns': {'C1': ['b']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C2': ['d']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            None, True, False),
                           ['Several linked lines match one main line,',
                            'but configuration says one line per main line']),
                          (dfa,
                           (MainLineSpec(data={'line': ['g', 'h'],
                                               'columns': {'C1': ['b']},
                                               'expand_at': []}),
                            MissingInputForColumn.ERROR,
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C2': ['d']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            LinkedLineSpec({'line': ['k'],
                                            'columns': {'C3': ['e']},
                                            'linked_column': ['f'],
                                            'linked_main_column': ['c'],
                                            'expand_at': []}),
                            True, False),
                           ['Several linked lines match one main line,',
                            'but configuration says one line per main line'])])
def test_extract_data_nok1(capsys: pytest.CaptureFixture[str],
                           ind: JsonType,
                           conf: tuple[MainLineSpec,
                                       MissingInputForColumn,
                                       LinkedLineSpec,
                                       Optional[LinkedLineSpec], bool, bool],
                           msgs: list[str]) -> None:
    """Test not OK cases 1 of extract_data."""
    main_line: MainLineSpec = conf[0]
    linked_spec: LinkedLineSpec = conf[2]
    linked_spec2: Optional[LinkedLineSpec] = conf[3]
    cfg = ExtractConfig()
    cfg.missing_input_for_column = conf[1]
    cfg.linked_lines = [linked_spec]
    if linked_spec2 is not None:
        cfg.linked_lines.append(linked_spec2)
    cfg.main_line = main_line
    cfg.one_output_line_per_main_line = conf[4]
    cfg.include_key = conf[5]
    with pytest.raises(SystemExit):
        _ = extract_data(indata=ind, cfg=cfg)
    check_capsys(capsys=capsys, in_err=msgs)
