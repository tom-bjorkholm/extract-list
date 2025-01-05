#! /usr/local/bin/python3
"""Test configuration file for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
from enum import Enum, auto
import pytest
from check_cfgs_equal import check_cfgs_equal
from check_capsys import check_capsys
from extract_list.extract_config import ExtractConfig, \
    MainLineSpec, MLineDict, _mline_spec_from_dict, \
    LinkedLineSpec, LLineDict, _linked_line_from_json_array
from extract_list.config_enums import InFileType, OutFileType


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_1(capsys, lin, col):
    """Test MainLineSprec (case 1)."""
    spec = MainLineSpec()
    spec.line = deepcopy(lin)
    spec.columns = deepcopy(col)
    txt = str(spec)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_2(capsys, lin, col):
    """Test MainLineSprec (case 2)."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'expand_at': []}
    spec = MainLineSpec(mld)
    txt = str(spec)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mlinespecfromdict(capsys, lin, col):
    """Test _mline_spec_from_dict."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'expand_at': []}
    spec = _mline_spec_from_dict(data=mld)
    txt = str(spec)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_linklinespec_1(capsys, lin, col, lmc, lcol):
    """Test LinkedLineSprec (case 1)."""
    spec = LinkedLineSpec()
    spec.line = deepcopy(lin)
    spec.columns = deepcopy(col)
    spec.linked_main_column = deepcopy(lmc)
    spec.linked_column = deepcopy(lcol)
    txt = str(spec)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_linklinespec_2(capsys,  # pylint: disable=too-many-locals
                        lin, col, lmc, lcol):
    """Test LinkedLineSprec (case 2)."""
    lld: LLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'linked_main_column': deepcopy(lmc),
                      'linked_column': deepcopy(lcol),
                      'expand_at': []}
    spec = LinkedLineSpec(data=lld)
    txt = str(spec)
    check_capsys(capsys=capsys)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    assert lin == spec.line
    assert col == spec.columns
    assert lmc == spec.linked_main_column
    assert lcol == spec.linked_column


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_llinefromjson(capsys,  # pylint: disable=too-many-locals
                       lin, col, lmc, lcol):
    """Test _linked_line_from_json_array."""
    lld: LLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'linked_main_column': deepcopy(lmc),
                      'linked_column': deepcopy(lcol),
                      'expand_at': []}
    speclist = _linked_line_from_json_array(data=[lld, lld])
    assert len(speclist) == 2
    assert speclist[0].line == speclist[1].line
    assert speclist[0].linked_column == speclist[1].linked_column
    assert speclist[0].linked_main_column == speclist[1].linked_main_column
    spec = speclist[0]
    txt = str(spec)
    check_capsys(capsys=capsys)
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    assert lin == spec.line
    assert col == spec.columns
    assert lmc == spec.linked_main_column
    assert lcol == spec.linked_column


@pytest.mark.parametrize('cols, order_row, res',
                         [(['a', 'b'], ['d', 'e'], ['d', 'e']),
                          (['a', 'b'], [], ['a', 'b'])])
def test_get_order_rows_by(capsys, cols, order_row, res):
    """Test get_order_rows_by."""
    cfg = ExtractConfig()
    cfg.column_order = cols
    cfg.order_rows_by = order_row
    ret = cfg.get_order_rows_by()
    assert ret == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('main, rworder',
                         [({'ab': ['cd', 'ef'], 'gh': ['ij']}, ['ab', 'gh']),
                          ({'kl': ['mn'], 'op': ['q', 'r']}, ['op'])])
@pytest.mark.parametrize('linked',
                         [[ExtractConfig.example_linked_line()]])
@pytest.mark.parametrize('keyinc', [True, False])
def test_cross_check_columns_ok(capsys, main, rworder, linked, keyinc):
    """Test OK case(s) of cross_check_columns."""
    col_order: list[str] = deepcopy(list(main.keys()))
    for elem in linked:
        col_order += deepcopy(list(elem.columns.keys()))
    if keyinc:
        col_order.append('key col')
    cfg = ExtractConfig()
    cfg.include_key = keyinc
    cfg.main_line.columns = main
    cfg.linked_lines = linked
    cfg.column_order = col_order
    cfg.order_rows_by = rworder
    cfg.cross_check_columns()
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('main, link, col, orw, errmsg',
                         [(MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []},
                                              'expand_at': []}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': [],
                               'expand_at': []
                           })], ['a', 'b', 'd'], [],
                           'Extracted column "c" is missing'),
                          (MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []},
                                              'expand_at': []}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': [],
                               'expand_at': []
                           })], ['a', 'c', 'd'], [],
                           'Extracted column "b" is missing'),
                          (MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []},
                                              'expand_at': []}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': [],
                               'expand_at': []})],
                           ['a', 'b', 'k', 'c', 'd'], [],
                           'includes column "k"\nbut that column is not ex'),
                          (MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []},
                                              'expand_at': []}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': [],
                               'expand_at': []
                           })], ['a', 'b', 'c', 'd'], ['c', 'b', 'f'],
                           'order rows by includes column "f"\nbut that')])
def test_cross_check_columns_nok(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                                 main, link, col, orw, errmsg):
    """Test not OK case(s) of cross_check_columns."""
    cfg = ExtractConfig()
    cfg.main_line = main
    cfg.linked_lines = link
    cfg.column_order = col
    cfg.order_rows_by = orw
    cfg.include_key = False
    with pytest.raises(SystemExit):
        cfg.cross_check_columns()
    check_capsys(capsys=capsys, in_err=errmsg)


def test_check_extr_uniq_col_ok1(capsys):
    """Test OK case 1 of check_extract_unique_colnames."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1'], 'b': ['b1']}
    cfg.linked_lines = []
    for ival in range(5):
        lls = LinkedLineSpec(data={'line': ['i'+str(ival)],
                                   'linked_column': ['b'],
                                   'linked_main_column': ['c'],
                                   'columns': {},
                                   'expand_at': []})
        for cnum in range(10, 13):
            lls.columns['c' + str(cnum) + '_' + str(ival)] = ['d', str(cnum)]
        cfg.linked_lines.append(lls)
    cfg.check_extract_unique_colnames()
    check_capsys(capsys=capsys)


def test_check_extr_uniq_col_nok1(capsys):
    """Test not OK case 1 of check_extract_unique_colnames."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1'], 'b': ['b1']}
    cfg.linked_lines = []
    lls = LinkedLineSpec(data={'line': ['i'],
                               'linked_column': ['b'],
                               'linked_main_column': ['c'],
                               'columns': {'c': ['c1'], 'b': ['d2']},
                               'expand_at': []})
    cfg.linked_lines.append(lls)
    with pytest.raises(SystemExit):
        cfg.check_extract_unique_colnames()
    errmsg = [
        'Column names of extracted data must be unique',
        'Repeated column name(s): b'
    ]
    check_capsys(capsys=capsys, in_err=errmsg)


def test_check_csv_ok(capsys):
    """Test OK case of check_csv."""
    cfg = ExtractConfig()
    cfg.out_csv_dialect = {'name': 'csv.unix_dialect',
                           'delimiter': ',', 'quoting': None,
                           'quotechar': '"',
                           'lineterminator': None,
                           'escapechar': None}
    cfg.check_csv()
    check_capsys(capsys=capsys)


def test_check_csv_nok1(capsys):
    """Test not OK case 1 of check_csv."""
    cfg = ExtractConfig()
    cfg.out_csv_dialect = {'name': 'csv.unix_dialects',
                           'delimiter': ',', 'quoting': None,
                           'quotechar': '"',
                           'lineterminator': None,
                           'escapechar': None}
    with pytest.raises(SystemExit):
        cfg.check_csv()
    errmsg = ['Configured out_csv_dialect is not valid',
              'Unknown csv dialect: csv.unix_dialects']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_check_csv_nok2(capsys):
    """Test not OK case 2 of check_csv."""
    cfg = ExtractConfig()
    cfg.out_csv_dialect = {'name': 'csv.unix_dialect',
                           'dellimiter': ',', 'quoting': None,
                           'quotechar': '"',
                           'lineterminator': None,
                           'escapechar': None}
    with pytest.raises(SystemExit):
        cfg.check_csv()
    errmsgs = ['Configured out_csv_dialect is not valid',
               "unexpected keyword argument 'dellimiter'"]
    check_capsys(capsys=capsys, in_err=errmsgs)


@pytest.mark.parametrize('var, varname',
                         [(['a', 'b', 'c'], 'abc'),
                          (['hello world'], 'hw')])
def test_check_list_str_ok(capsys, var, varname):
    """Test OK cases of _check_list_str."""
    ExtractConfig._check_list_str(var=var,  # pylint: disable=protected-access
                                  varname=varname)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('var,name,msg',
                         [('str', 'abc',
                           ['Expected a list of strings in abc',
                            'of type str']),
                          (2, 'def',
                           ['Expected a list of strings in def',
                            'of type int']),
                          ([2], 'ghi',
                           ['Expected a list of strings in ghi',
                            'of type int',
                            'but found element: 2']),
                          (['str', [2]], 'jkl',
                           ['Expected a list of strings in jkl',
                            'of type list',
                            'but found element: [2]'])])
def test_check_list_str_nok(capsys, var, name, msg):
    """Test not OK cases of _check_list_str."""
    with pytest.raises(SystemExit):
        ExtractConfig._check_list_str(var=var,  # pylint: disable=protected-access  # noqa: E501
                                      varname=name)
    check_capsys(capsys=capsys, in_err=msg)


@pytest.mark.parametrize('val,typ,name',
                         [(1, int, 'x'), ('ab', str, 'y'),
                          ([2], list, 'z')])
def test_check_type_ok(capsys, val, typ, name):
    """Test OK cases for _check_type."""
    ExtractConfig._check_type(var=val,  # pylint: disable=protected-access
                              oftype=typ, varname=name)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('val,typ,name, msgs',
                         [(1, str, 'x',
                           ['Configuration parameter "x" has wrong type',
                            'Type is "int"',
                            'but expected type "str"']),
                          ('ab', int, 'y',
                           ['Configuration parameter "y" has wrong type',
                            'Type is "str"',
                            'but expected type "int"']),
                          ([2], int, 'z',
                           ['Configuration parameter "z" has wrong type',
                            'Type is "list"',
                            'but expected type "int"']),
                          ('abc', list, 'p',
                           ['Configuration parameter "p" has wrong type',
                            'Type is "str"',
                            'but expected type "list"'])])
def test_check_type_nok(capsys, val, typ, name, msgs):
    """Test not OK cases for _check_type."""
    with pytest.raises(SystemExit):
        ExtractConfig._check_type(var=val,  # pylint: disable=protected-access
                                  oftype=typ, varname=name)
    check_capsys(capsys=capsys, in_err=msgs)


class Abc(Enum):
    """Enum just for testing."""

    AA1 = auto()
    BB2 = auto()
    CC3 = auto()


class Ghj(Enum):
    """Enum just for testing."""

    AA1 = auto()
    BB2 = auto()
    CC3 = auto()
    GG4 = auto()


@pytest.mark.parametrize('val', list(Abc))
@pytest.mark.parametrize('name', ['name1', 'name2'])
def test_check_enum_ok(capsys, val, name):
    """Test OK cases for _check_enum."""
    ExtractConfig._check_enum(var=val,  # pylint: disable=protected-access
                              enum_type=Abc, varname=name)
    check_capsys(capsys=capsys)


def test_check_enum_nok1(capsys):
    """Test not OK cases for _check_enum."""
    val = Ghj.GG4
    with pytest.raises(SystemExit):
        ExtractConfig._check_enum(var=val,  # pylint: disable=protected-access
                                  enum_type=Abc, varname='name1')
    msgs = ['Configuration parameter "name1" has wrong type',
            'Type is "Ghj", but expected type "Abc".']
    check_capsys(capsys=capsys, in_err=msgs)


@pytest.mark.parametrize('name', ['abc', 'def'])
@pytest.mark.parametrize('dval',
                         [{'ab': [], 'de': ['ef', 'gh']},
                          {'zx': ['abc', 'def']},
                          {'as': []}])
def test_check_dict_str_lst_ok(capsys, name, dval):
    """Test OK cases of _check_dict_str_lst_str."""
    ExtractConfig._check_dict_str_lst_str(var=dval,  # pylint: disable=protected-access # noqa: E501
                                          varname=name)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('val,name,errmsgs',
                         [(2, 'abc',
                           ['Expected a dict of strings to lists in abc',
                            'but found: 2', 'of type int']),
                          ({3: []}, 'def',
                           ['Expected a dict of strings to lists in def',
                            'but found key: 3', 'of type int']),
                          ({4: ['ab', 'cd']}, 'de',
                           ['Expected a dict of strings to lists in de',
                            'but found key: 4', 'of type int']),
                          ({'x': ['ab', 'cd'], 5: []}, 'fg',
                           ['Expected a dict of strings to lists in fg',
                            'but found key: 5', 'of type int']),
                          ({'ab': {'cd': []}}, 'hj',
                           ['Expected a list of strings in ab in hj',
                            'but found: {\'cd\': []}', 'of type dict']),
                          ({'ab': [1, 2]}, 'kl',
                           ['Expected a list of strings in ab in kl',
                            'but found element: 1', 'of type int']),
                          ])
def test_check_dict_str_lst_nok(capsys, val, name, errmsgs):
    """Test not OK cases of _check_dict_str_lst_str."""
    with pytest.raises(SystemExit):
        ExtractConfig._check_dict_str_lst_str(var=val,  # pylint: disable=protected-access # noqa: E501
                                              varname=name)
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_mainline_part_ok1(capsys):
    """Test OK case 1 of _check_main_line_part."""
    a = MainLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    ExtractConfig._check_mainline_part(a,  # pylint: disable=protected-access # noqa: E501
                                       MainLineSpec, 'a')
    check_capsys(capsys=capsys)


def test_check_mainline_part_ok2(capsys):
    """Test OK case 2 of _check_main_line_part."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    ExtractConfig._check_mainline_part(a,  # pylint: disable=protected-access # noqa: E501
                                       LinkedLineSpec, 'a')
    check_capsys(capsys=capsys)


def test_check_mainline_part_nok1(capsys):
    """Test not OK case 1 of _check_main_line_part."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_mainline_part(a,  # pylint: disable=protected-access # noqa: E501
                                           MainLineSpec, 'a')
    errmsgs = ['Expected MainLineSpec for a, but found',
               'of type LinkedLineSpec']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_mainline_part_nok2(capsys):
    """Test not OK case 2 of _check_main_line_part."""
    a = MainLineSpec()
    a.line = [1, 2]
    a.columns = {'name': ['ef'], 'address': ['gh']}
    with pytest.raises(SystemExit):
        ExtractConfig._check_mainline_part(a,  # pylint: disable=protected-access # noqa: E501
                                           MainLineSpec, 'a')
    errmsgs = ['Expected a list of strings in line in a',
               'but found element: 1', 'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_mainline_part_nok3(capsys):
    """Test not OK case 3 of _check_main_line_part."""
    a = MainLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': [1], 'address': ['gh']}
    with pytest.raises(SystemExit):
        ExtractConfig._check_mainline_part(a,  # pylint: disable=protected-access # noqa: E501
                                           MainLineSpec, 'a')
    errmsgs = ['Expected a list of strings in name in columns in a',
               'but found element: 1', 'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_ok1(capsys):
    """Test OK case 1 of _check_linkedline."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    ExtractConfig._check_linkedline([a],  # pylint: disable=protected-access # noqa: E501
                                    'a')
    check_capsys(capsys=capsys)


def test_check_linkedline_nok0(capsys):
    """Test not OK case 0 of _check_linkedline."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline(a,  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = ['Expected a list of LinkedLineSpec in a',
               'of type LinkedLineSpec']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_nok1(capsys):
    """Test not OK case 1 of _check_linked."""
    a = MainLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline([a],  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = ['Expected LinkedLineSpec for element in a, but found:',
               'of type MainLineSpec']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_nok2(capsys):
    """Test not OK case 3 of _check_linked."""
    a = LinkedLineSpec()
    a.line = ['ab', 2]
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline([a],  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = ['Expected a list of strings in line in element in a',
               'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_nok3(capsys):
    """Test not OK case 3 of _check_linked."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 4, 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline([a],  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = [
        'Expected a list of strings in linked_main_column in element in a',
        'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_nok4(capsys):
    """Test not OK case 4 of _check_linked."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 7]
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline([a],  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = ['Expected a list of strings in linked_column in element in a',
               'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_check_linkedline_nok5(capsys):
    """Test not OK case 5 of _check_linkedline."""
    a = LinkedLineSpec()
    a.line = ['ab', 'cd']
    a.columns = {'name': ['ef'], 'address': ['gh']}
    a.linked_main_column = ['xy', 'ab', 'cd', 'ef']
    a.linked_column = ['ab', 'cd', 'ef']
    with pytest.raises(SystemExit):
        ExtractConfig._check_linkedline([a, 2],  # pylint: disable=protected-access # noqa: E501
                                        'a')
    errmsgs = ['Expected LinkedLineSpec for element in a',
               'of type int']
    check_capsys(capsys=capsys, in_err=errmsgs)


@pytest.mark.parametrize('fval', list(InFileType))
def test_check_filetype_ok1(capsys, fval):
    """Test OK cases 1 of _check_filetype."""
    ExtractConfig._check_filetype(fval,  # pylint: disable=protected-access # noqa: E501
                                  InFileType)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('fval', list(OutFileType))
def test_check_filetype_ok(capsys, fval):
    """Test OK cases  2 of _check_filetype."""
    ExtractConfig._check_filetype(fval,  # pylint: disable=protected-access # noqa: E501
                                  OutFileType)
    check_capsys(capsys=capsys)


def test_check_filetype_nok1(capsys):
    """Test not OK case 1 of _check_filetype."""
    with pytest.raises(SystemExit):
        ExtractConfig._check_filetype(1,  # pylint: disable=protected-access # noqa: E501
                                      OutFileType)
    check_capsys(capsys=capsys,
                 in_err='File type 1 is not of type OutFileType')


@pytest.mark.parametrize('attr',
                         [['What'], ['Street'],
                          ['How many', 'Street number']])
def test_cross_check_attrs_ok(capsys, attr):
    """Test OK case of cross_check_attrs."""
    cfg = ExtractConfig()
    cfg.out_xml_attributes = attr
    cfg.cross_check_attrs()
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('attr, errmsgs',
                         [(['Where'],
                           ['Attribute name "Where" in out_xml_attributes']),
                          (['Road'],
                           ['Attribute name "Road" in out_xml_attributes']),
                          (['How many', 'Street number', 'abc'],
                           ['Attribute name "abc" in out_xml_attributes'])])
def test_cross_check_attrs_nok(capsys, attr, errmsgs):
    """Test OK case of cross_check_attrs."""
    cfg = ExtractConfig()
    cfg.out_xml_attributes = attr
    with pytest.raises(SystemExit):
        cfg.cross_check_attrs()
    checkmsg = deepcopy(errmsgs)
    checkmsg.append('but no column with that name extracted')
    check_capsys(capsys=capsys, in_err=checkmsg)


def test_extract_config_nochange(capsys):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    check_capsys(capsys=capsys)
