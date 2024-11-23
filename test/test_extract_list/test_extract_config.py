#! /usr/local/bin/python3
"""Test configuration file for extract list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

# import sys
# from tempfile import TemporaryDirectory
from copy import deepcopy
from enum import Enum, auto
import pytest
from extract_list.config_enums import InFileType, OutFileType
from extract_list.extract_config import ExtractConfig, \
    MainLineSpec, MLineDict, _mline_spec_from_dict, \
    LinkedLineSpec, LLineDict, _linked_line_from_json_array


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
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_2(capsys, lin, col):
    """Test MainLineSprec (case 2)."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col)}
    spec = MainLineSpec(mld)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mlinespecfromdict(capsys, lin, col):
    """Test _mline_spec_from_dict."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col)}
    spec = _mline_spec_from_dict(data=mld)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    assert '' == out
    assert '' == err


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
    out, err = capsys.readouterr()
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
    assert '' == out
    assert '' == err


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
                      'linked_column': deepcopy(lcol)}
    spec = LinkedLineSpec(data=lld)
    txt = str(spec)
    out, err = capsys.readouterr()
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
    assert '' == out
    assert '' == err


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
                      'linked_column': deepcopy(lcol)}
    speclist = _linked_line_from_json_array(data=[lld, lld])
    assert len(speclist) == 2
    assert speclist[0].line == speclist[1].line
    assert speclist[0].linked_column == speclist[1].linked_column
    assert speclist[0].linked_main_column == speclist[1].linked_main_column
    spec = speclist[0]
    txt = str(spec)
    out, err = capsys.readouterr()
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
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('main',
                         [{'ab': ['cd', 'ef'], 'gh': ['ij']},
                          {'kl': ['mn'], 'op': ['q', 'r']}])
@pytest.mark.parametrize('linked',
                         [[ExtractConfig.example_linked_line()]])
@pytest.mark.parametrize('keyinc', [True, False])
def test_cross_check_columns_ok(capsys, main, linked, keyinc):
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
    cfg.cross_check_columns()
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('main, link, col, errmsg',
                         [(MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []}}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': []
                           })], ['a', 'b', 'd'],
                           'Extracted column "c" is missing'),
                          (MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []}}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': []
                           })], ['a', 'c', 'd'],
                           'Extracted column "b" is missing'),
                          (MainLineSpec(data={'line': [],
                                              'columns': {'a': [], 'b': []}}),
                           [LinkedLineSpec(data={
                               'line': [],
                               'columns': {'c': [], 'd': []},
                               'linked_column': [],
                               'linked_main_column': []
                           })], ['a', 'b', 'k', 'c', 'd'],
                           'includes column "k"\nbut that column is not ex')])
def test_cross_check_columns_nok(capsys, main, link, col, errmsg):
    """Test not OK case(s) of cross_check_columns."""
    cfg = ExtractConfig()
    cfg.main_line = main
    cfg.linked_lines = link
    cfg.column_order = col
    cfg.include_key = False
    with pytest.raises(SystemExit):
        cfg.cross_check_columns()
    out, err = capsys.readouterr()
    assert errmsg in err
    assert '' == out


def test_check_csv_ok(capsys):
    """Test OK case of check_csv."""
    cfg = ExtractConfig()
    cfg.out_csv_dialect = {'name': 'csv.unix_dialect',
                           'delimiter': ',', 'quoting': None,
                           'quotechar': '"',
                           'lineterminator': None,
                           'escapechar': None}
    cfg.check_csv()
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


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
    out, err = capsys.readouterr()
    assert 'Configured out_csv_dialect is not valid' in err
    assert 'Unknown csv dialect: csv.unix_dialects' in err
    assert '' == out


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
    out, err = capsys.readouterr()
    assert 'Configured out_csv_dialect is not valid' in err
    assert "unexpected keyword argument 'dellimiter'" in err
    assert '' == out


@pytest.mark.parametrize('var, varname',
                         [(['a', 'b', 'c'], 'abc'),
                          (['hello world'], 'hw')])
def test_check_list_str_ok(capsys, var, varname):
    """Test OK cases of _check_list_str."""
    ExtractConfig._check_list_str(var=var,  # pylint: disable=protected-access
                                  varname=varname)
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


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
    out, err = capsys.readouterr()
    assert '' == out
    for msg_elem in msg:
        assert msg_elem in err


@pytest.mark.parametrize('val,typ,name',
                         [(1, int, 'x'), ('ab', str, 'y'),
                          ([2], list, 'z')])
def test_check_type_ok(capsys, val, typ, name):
    """Test OK cases for _check_type."""
    ExtractConfig._check_type(var=val,  # pylint: disable=protected-access
                              oftype=typ, varname=name)
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


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
    out, err = capsys.readouterr()
    assert '' == out
    for single_msg in msgs:
        assert single_msg in err


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
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


def test_check_enum_nok1(capsys):
    """Test not OK cases for _check_enum."""
    val = Ghj.GG4
    with pytest.raises(SystemExit):
        ExtractConfig._check_enum(var=val,  # pylint: disable=protected-access
                                  enum_type=Abc, varname='name1')
    out, err = capsys.readouterr()
    assert '' == out
    assert 'Configuration parameter "name1" has wrong type' in err
    assert 'Type is "Ghj", but expected type "Abc".' in err


@pytest.mark.parametrize('name', ['abc', 'def'])
@pytest.mark.parametrize('dval',
                         [{'ab': [], 'de': ['ef', 'gh']},
                          {'zx': ['abc', 'def']},
                          {'as': []}])
def test_check_dict_str_lst_ok(capsys, name, dval):
    """Test OK cases of _check_dict_str_lst_str."""
    ExtractConfig._check_dict_str_lst_str(var=dval,  # pylint: disable=protected-access # noqa: E501
                                          varname=name)
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


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
    out, err = capsys.readouterr()
    assert '' == out
    for msg in errmsgs:
        assert msg in err


# TODO test check methods: _check_mainline_part
# TODO test check methods: _check_linkedline
# TODO test check methods: _check_filetype


def test_extract_config_nochange(capsys):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    assert cfg.infile_type == cf2.infile_type
    assert cfg.infile_encoding == cf2.infile_encoding
    assert cfg.in_xml_strip_at == cf2.in_xml_strip_at
    assert cfg.include_key == cf2.include_key
    assert cfg.column_name_for_key == cf2.column_name_for_key
    assert cfg.missing_input_for_column == cf2.missing_input_for_column
    assert cfg.main_line.line == cf2.main_line.line
    assert cfg.main_line.columns == cf2.main_line.columns
    assert len(cfg.linked_lines) == len(cf2.linked_lines)
    for elem1, elem2 in zip(cfg.linked_lines, cf2.linked_lines):
        assert elem1.line == elem2.line
    assert cfg.outfile_type == cf2.outfile_type
    assert cfg.outfile_encoding == cf2.outfile_encoding
    assert cfg.outfile_excel_library == cf2.outfile_excel_library
    assert cfg.column_order == cf2.column_order
    assert cfg.out_xml_attributes == cf2.out_xml_attributes
    assert cfg.out_csv_dialect == cf2.out_csv_dialect
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         [OutFileType.JSON, OutFileType.XML, OutFileType.CSV,
                          OutFileType.EXCEL, OutFileType.TXT])
def test_extract_config_var1(capsys, inenc, infiletype, outenc, outfiletype):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.outfile_encoding = deepcopy(outenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.outfile_type = deepcopy(outfiletype)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    assert cf2.infile_type == infiletype
    assert cfg.infile_type == cf2.infile_type
    assert cf2.infile_encoding == inenc
    assert cfg.infile_encoding == cf2.infile_encoding
    assert cfg.in_xml_strip_at == cf2.in_xml_strip_at
    assert cfg.include_key == cf2.include_key
    assert cfg.column_name_for_key == cf2.column_name_for_key
    assert cfg.missing_input_for_column == cf2.missing_input_for_column
    assert cfg.main_line.line == cf2.main_line.line
    assert cfg.main_line.columns == cf2.main_line.columns
    assert len(cfg.linked_lines) == len(cf2.linked_lines)
    for elem1, elem2 in zip(cfg.linked_lines, cf2.linked_lines):
        assert elem1.line == elem2.line
    assert cf2.outfile_type == outfiletype
    assert cfg.outfile_type == cf2.outfile_type
    assert cf2.outfile_encoding == outenc
    assert cfg.outfile_encoding == cf2.outfile_encoding
    assert cfg.outfile_excel_library == cf2.outfile_excel_library
    assert cfg.column_order == cf2.column_order
    assert cfg.out_xml_attributes == cf2.out_xml_attributes
    assert cfg.out_csv_dialect == cf2.out_csv_dialect
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


# TODO test variations of valid configuraitons
# TODO test messages for variations of invalid configurations
