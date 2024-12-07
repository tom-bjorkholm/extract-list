#! /usr/local/bin/python3
"""Test configuration file for extract list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from copy import deepcopy
import pytest
from extract_list.config_enums import MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_func import get_at_path, \
    get_lines, get_columns, extract_main_line, MainDataLine, \
    extract_data, create_none_columns

da1 = {'ab': 'c', 'de': 'g', 'fg': 9}
da2 = {'ax': 'h', 'bx': 'ij', 'cx': 7}
db1 = {'xq': da1, 'xw': 'kl', 'xe': da2}
db2 = {'yq': {'mn': 6, 'op': da2}, 'yw': 4, 'ye': {'za': 2, 'zb': da2}}
dc1 = {'qa': 3, 'qb': db1, 'qc': 'rst', 'qd': db2}


@pytest.mark.parametrize('mis',
                         [MissingInputForColumn.EMPTY,
                          MissingInputForColumn.ERROR])
@pytest.mark.parametrize('ind,pat,res',
                         [(da1, ['de'], 'g'),
                          (db1, ['xe', 'bx'], 'ij'),
                          (db2, ['yq', 'op'], da2),
                          (dc1, ['qb', 'xq', 'fg'], 9)])
def test_get_at_path_ok1(capsys, mis, ind, pat, res):
    """Test OK cases 1 of get_at_path."""
    ret = get_at_path(indata=deepcopy(ind), path=pat, missing=mis)
    out, err = capsys.readouterr()
    assert ret == res
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('ind,pat,res',
                         [(da1, ['dq'], None),
                          (db1, ['xe', 'bxx'], None),
                          (db2, ['yq', 'op', 'ff'], None),
                          (dc1, ['qb', 'xq', 'fg'], 9)])
def test_get_at_path_ok2(capsys, ind, pat, res):
    """Test OK cases 2 of get_at_path."""
    ret = get_at_path(indata=deepcopy(ind), path=pat,
                      missing=MissingInputForColumn.EMPTY)
    out, err = capsys.readouterr()
    assert ret == res
    assert '' == out
    assert '' == err


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
def test_get_at_path_nok1(capsys, mis, ind, pat, msgs):
    """Test OK cases 1 of get_at_path."""
    with pytest.raises(SystemExit):
        _ = get_at_path(indata=deepcopy(ind), path=pat, missing=mis)
    out, err = capsys.readouterr()
    assert '' == out
    for errmsg in msgs:
        assert errmsg in err


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
def test_get_at_path_nok2(capsys, ind, pat, msgs):
    """Test OK cases 1 of get_at_path."""
    with pytest.raises(SystemExit):
        _ = get_at_path(indata=deepcopy(ind), path=pat,
                        missing=MissingInputForColumn.ERROR)
    out, err = capsys.readouterr()
    assert '' == out
    for errmsg in msgs:
        assert errmsg in err


dd1 = {'a': 'bc', 'b': 'de', 'c': 4}
dd2 = {'a': 'fg', 'b': 'hi', 'c': 5}
dd3 = {'a': 'jk', 'b': 'lm', 'c': 6}
dd4 = {'a': 'no', 'b': 'pq', 'c': 7}
de1 = {'d': 'abc', 'e': 'def', 'f': 4}
de2 = {'d': 'ghi', 'e': 'jkl', 'f': 5}
de3 = {'d': 'mno', 'e': 'pqr', 'f': 6}
de4 = {'d': 'stu', 'e': 'vwx', 'f': 6}
de5 = {'d': 'yza', 'e': 'bcd', 'f': 7}
de6 = {'d': 'efg', 'e': 'hij', 'f': 7}
dda = [dd1, dd2, dd3, dd4]
dea = [de1, de2, de3, de4, de5, de6]
ddm = {'d1': dd1, 'd2': dd2, 'd3': dd3, 'd4': dd4}
dem = {'e1': de1, 'e2': de2, 'e3': de3, 'e4': de4, 'e5': de5, 'e6': de6}
dfa = {'g': {'h': dda}, 'k': dea}
dfm = {'g': {'h': ddm}, 'k': dem}


@pytest.mark.parametrize('mis', [MissingInputForColumn.EMPTY,
                                 MissingInputForColumn.ERROR])
@pytest.mark.parametrize('inp,pat,res',
                         [(dfa, ['g', 'h'], dda),
                          (dfa, ['k'], dea),
                          (dfm, ['g', 'h'], dda),
                          (dfm, ['k'], dea),
                          (dfm, ['k', 'e1', 'f'], [4])])
def test_get_lines_ok1(capsys, mis, inp, pat, res):
    """Test OK cases 1 for get_lines."""
    result = deepcopy(res)
    counter = 0
    for index, (_, line) in enumerate(get_lines(indata=deepcopy(inp),
                                                missing=mis, path=pat)):
        assert line == result[index]
        counter += 1
    assert len(result) == counter
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('inp,pat',
                         [(dfa, ['g', 'k']),
                          (dfa, ['m']),
                          (dfm, ['g', 'h', 'x']),
                          (dfm, ['k', 'e47']),
                          (dfm, ['k', 'e1', 'g'])])
def test_get_lines_ok2(capsys, inp, pat):
    """Test OK cases 2 for get_lines."""
    counter = 0
    for index, (_, line) in \
        enumerate(get_lines(indata=deepcopy(inp),
                            missing=MissingInputForColumn.EMPTY,
                            path=pat)):
        assert line is None
        counter += 1
        assert 0 == index
    assert 1 == counter
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('inp,pat',
                         [(dfa, ['g', 'k']),
                          (dfa, ['m']),
                          (dfm, ['g', 'h', 'x']),
                          (dfm, ['k', 'e47']),
                          (dfm, ['k', 'e1', 'g'])])
def test_get_lines_nok1(capsys, inp, pat):
    """Test not OK cases 1 for get_lines."""
    counter = 0
    with pytest.raises(SystemExit):
        for index, (_, line) in \
            enumerate(get_lines(indata=deepcopy(inp),
                                missing=MissingInputForColumn.ERROR,
                                path=pat)):
            assert line is None
            counter += 1
            assert 0 == index
    assert 0 == counter
    out, err = capsys.readouterr()
    assert '' == out
    assert 'No such key ' in err
    assert ' in relevant section' in err


@pytest.mark.parametrize('inp, pat',
                         [({'a':
                            {MissingInputForColumn.EMPTY: {'b': 1, 'c': 2},
                             MissingInputForColumn.ERROR: {'b': 4, 'c': 5}}},
                           ['a'])])
def test_get_lines_nok2(capsys, inp, pat):
    """Test not OK cases 2 for get_lines."""
    counter = 0
    with pytest.raises(SystemExit):
        for index, (_, line) in \
            enumerate(get_lines(indata=deepcopy(inp),
                                missing=MissingInputForColumn.EMPTY,
                                path=pat)):
            assert line is None
            counter += 1
            assert 0 == index
    assert 0 == counter
    out, err = capsys.readouterr()
    assert '' == out
    assert 'Key "MissingInputForColumn.EMPTY" is not str' in err
    assert ' is not str or int as expected' in err


@pytest.mark.parametrize('mis', [MissingInputForColumn.EMPTY,
                                 MissingInputForColumn.ERROR])
@pytest.mark.parametrize('inp,spec,res',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['a']},
                           {'x': 'de', 'y': 4, 'z': 'bc'}),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'c']},
                           {'c1': 'de', 'c2': 5})])
def test_get_columns_ok1(capsys, mis, inp, spec, res):
    """Test OK cases 1 of get_columns."""
    ret = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                      missing=mis)
    out, err = capsys.readouterr()
    assert res == ret
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('inp,spec,res',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['d']},
                           {'x': 'de', 'y': 4, 'z': None}),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'cc']},
                           {'c1': 'de', 'c2': None})])
def test_get_columns_ok2(capsys, inp, spec, res):
    """Test OK cases 2 of get_columns."""
    ret = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                      missing=MissingInputForColumn.EMPTY)
    out, err = capsys.readouterr()
    assert res == ret
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('inp,spec,msg',
                         [(dd1, {'x': ['b'], 'y': ['c'], 'z': ['d']},
                           'No such key "d"'),
                          (ddm, {'c1': ['d1', 'b'], 'c2': ['d2', 'cc']},
                           'No such key "cc"')])
def test_get_columns_nok1(capsys, inp, spec, msg):
    """Test not OK cases 1 of get_columns."""
    with pytest.raises(SystemExit):
        _ = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                        missing=MissingInputForColumn.ERROR)
    out, err = capsys.readouterr()
    assert msg in err
    assert '' == out
    assert '" in relevant section in input data.' in err


@pytest.mark.parametrize('inp,spec,msg',
                         [(dfa, {'x': ['g', 'h'], 'y': 'k'},
                           "Expected a single value for x at ['g', 'h']"),
                          (ddm, {'c1': ['d1'], 'c2': ['d3']},
                           "Expected a single value for c1 at ['d1']")])
def test_get_columns_nok2(capsys, inp, spec, msg):
    """Test not OK cases 2 of get_columns."""
    with pytest.raises(SystemExit):
        _ = get_columns(inline=deepcopy(inp), colspec=deepcopy(spec),
                        missing=MissingInputForColumn.ERROR)
    out, err = capsys.readouterr()
    assert msg in err
    assert '' == out
    assert 'but found data of type' in err


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
def test_extract_main_line_ok1(capsys, tax):
    """Test OK cases 1 of extract_main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = tax[3]
    cfg.main_line.line = tax[1]
    cfg.main_line.columns = tax[2]
    cfg.include_key = tax[4]
    cfg.column_name_for_key = tax[5]
    for ret, expected in zip(extract_main_line(indata=tax[0],
                                               cfg=cfg), tax[6]):
        exp_main = MainDataLine(**expected)
        assert ret.complete_line == exp_main.complete_line
        assert ret.key == exp_main.key
        assert ret.row == exp_main.row
    num = 0
    for _ in extract_main_line(indata=tax[0], cfg=cfg):
        num += 1
    assert num == len(tax[6])
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


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
def test_extract_main_line_nok1(capsys, tbx, msgs):
    """Test not OK cases 1 of extract_main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = tbx[3]
    cfg.main_line.line = tbx[1]
    cfg.main_line.columns = tbx[2]
    cfg.include_key = tbx[4]
    cfg.column_name_for_key = tbx[5]
    with pytest.raises(SystemExit):
        for _ in extract_main_line(indata=tbx[0], cfg=cfg):
            pass
    out, err = capsys.readouterr()
    assert '' == out
    for msg in msgs:
        assert msg in err


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
def test_extract_data_mainline_ok1(capsys, tcx):
    """Test OK cases 1 of extract_data for main_line."""
    cfg = ExtractConfig()
    cfg.missing_input_for_column = tcx[3]
    cfg.main_line.line = tcx[1]
    cfg.main_line.columns = tcx[2]
    cfg.include_key = tcx[4]
    cfg.column_name_for_key = tcx[5]
    cfg.linked_lines = []
    res = extract_data(indata=deepcopy(tcx[0]), cfg=cfg)
    out, err = capsys.readouterr()
    assert res == tcx[6]
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('spec,res',
                         [({}, {}),
                          ({'qwe': ['a', 'b'], 'asd': ['c']},
                           {'qwe': None, 'asd': None})])
def test_create_none_columns(capsys, spec, res):
    """Test create_none_columns."""
    ret = create_none_columns(colspec=deepcopy(spec))
    out, err = capsys.readouterr()
    assert res == ret
    assert '' == out
    assert '' == err
