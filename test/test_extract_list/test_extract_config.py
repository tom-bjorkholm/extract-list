#! /usr/local/bin/python3
"""Test configuration file for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
from typing import Optional
import json
import sys
import warnings
import pytest
from config_as_json import InvalidConfiguration
from tableio import CsvDialect
from tableio_cfg_json import TioJsonCsvConfig
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import \
    LineSpecBase, MainLineSpec, MLineDict, LinkedLineSpec, LLineDict
from .check_cfgs_equal import check_cfgs_equal
from .check_capsys import check_capsys


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_1(capsys: pytest.CaptureFixture[str], lin: list[str],
                        col: dict[str, list[str]]) -> None:
    """Test MainLineSpec (case 1)."""
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
def test_mainlinespec_2(capsys: pytest.CaptureFixture[str], lin: list[str],
                        col: dict[str, list[str]]) -> None:
    """Test MainLineSpec (case 2)."""
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
def test_mlinespec_json(capsys: pytest.CaptureFixture[str], lin: list[str],
                        col: dict[str, list[str]]) -> None:
    """Test MainLineSpec read from JSON."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'expand_at': []}
    spec = MainLineSpec(from_json_data_text=json.dumps(mld))
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
def test_linklinespec_1(capsys: pytest.CaptureFixture[str], lin: list[str],
                        col: dict[str, list[str]], lmc: list[str],
                        lcol: list[str]) -> None:
    """Test LinkedLineSpec (case 1)."""
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
def test_linklinespec_2(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-locals # noqa: E501
                        lin: list[str], col: dict[str, list[str]],
                        lmc: list[str], lcol: list[str]) -> None:
    """Test LinkedLineSpec (case 2)."""
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
def test_llinespec_json(capsys: pytest.CaptureFixture[str], lin: list[str],
                        col: dict[str, list[str]], lmc: list[str],
                        lcol: list[str]) -> None:
    """Test LinkedLineSpec read from JSON."""
    lld: LLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'linked_main_column': deepcopy(lmc),
                      'linked_column': deepcopy(lcol),
                      'expand_at': []}
    spec = LinkedLineSpec(from_json_data_text=json.dumps(lld))
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
def test_get_order_rows_by(capsys: pytest.CaptureFixture[str], cols: list[str],
                           order_row: list[str], res: list[str]) -> None:
    """Test get_order_rows_by."""
    cfg = ExtractConfig()
    cfg.column_order = cols
    cfg.order_rows_by = order_row
    ret = cfg.get_order_rows_by()
    assert ret == res
    check_capsys(capsys=capsys)


def test_old_cfg_hook_current(capsys: pytest.CaptureFixture[str]) -> None:
    """Test parsing uses the current config-as-json read-old hook."""
    cfg = ExtractConfig()
    text = cfg.as_json_string(stderr_file=sys.stderr)
    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        cf2 = ExtractConfig(from_json_data_text=text)
    check_cfgs_equal(cfg, cf2)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('main, rworder',
                         [({'ab': ['cd', 'ef'], 'gh': ['ij']}, ['ab', 'gh']),
                          ({'kl': ['mn'], 'op': ['q', 'r']}, ['op'])])
@pytest.mark.parametrize('linked', [[ExtractConfig.example_linked_line()]])
@pytest.mark.parametrize('keyinc', [True, False])
def test_cross_check_columns_ok(capsys: pytest.CaptureFixture[str],
                                main: dict[str, list[str]], rworder: list[str],
                                linked: list[LinkedLineSpec],
                                keyinc: bool) -> None:
    """Test OK case(s) of column reference validation."""
    col_order: list[str] = deepcopy(list(main.keys()))
    for elem in linked:
        col_order += deepcopy(list(elem.columns.keys()))
    if keyinc:
        col_order.append('key_col')
    cfg = ExtractConfig()
    cfg.include_key = keyinc
    cfg.main_line.columns = main
    cfg.linked_lines = linked
    cfg.column_order = col_order
    cfg.order_rows_by = rworder
    cfg.out_xml_attributes = []
    cfg.validate(stderr_file=sys.stderr)
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
                           'extracted column "c" is missing in column_order'),
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
                           'extracted column "b" is missing in column_order'),
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
                           'column_order includes column "k", but that '
                           'column is not extracted'),
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
                           'order_rows_by includes column "f", but that '
                           'column is not extracted')])
def test_cross_check_columns_nok(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                                 main: MainLineSpec,
                                 link: list[LinkedLineSpec], col: list[str],
                                 orw: list[str], errmsg: str) -> None:
    """Test not OK case(s) of column reference validation."""
    cfg = ExtractConfig()
    cfg.main_line = main
    cfg.linked_lines = link
    cfg.column_order = col
    cfg.order_rows_by = orw
    cfg.include_key = False
    cfg.out_xml_attributes = []
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err=errmsg)


@pytest.mark.parametrize('member, prefix', [(None, ''),
                                            ('extract', 'extract.')])
def test_column_refs_all(capsys: pytest.CaptureFixture[str],
                         member: Optional[str], prefix: str) -> None:
    """Test that every column reference problem is reported at once."""
    cfg = ExtractConfig()
    cfg.column_order = ['What', 'Bogus', 'Customer name', 'Street',
                        'Street number', 'key_col']
    cfg.order_rows_by = ['Sorter']
    cfg.out_xml_attributes = ['Attr']
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr, member_name=member)
    errmsg = [f'{prefix}column_order includes column "Bogus"',
              f'{prefix}order_rows_by includes column "Sorter"',
              f'{prefix}out_xml_attributes includes column "Attr"',
              'extracted column "How many" is missing in '
              f'{prefix}column_order']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_check_extr_uniq_col_ok1(capsys: pytest.CaptureFixture[str]) -> None:
    """Test OK case 1 of extracted column name validation."""
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
    cfg.column_order = [name for lls in cfg.linked_lines
                        for name in lls.columns] + ['a', 'b', 'key_col']
    cfg.out_xml_attributes = []
    cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys)


def test_check_extr_uniq_col_nok1(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK case 1 of extracted column name validation."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1'], 'b': ['b1']}
    cfg.linked_lines = []
    lls = LinkedLineSpec(data={'line': ['i'],
                               'linked_column': ['b'],
                               'linked_main_column': ['c'],
                               'columns': {'c': ['c1'], 'b': ['d2']},
                               'expand_at': []})
    cfg.linked_lines.append(lls)
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    errmsg = ['Extracted column names must be unique',
              'Repeated column name(s): b at linked_lines[0].columns[b], '
              'main_line.columns[b]']
    check_capsys(capsys=capsys, in_err=errmsg)


def _two_linked_lines(cfg: ExtractConfig, name: str) -> None:
    """Give cfg two linked lines that both extract the column name."""
    cfg.linked_lines = []
    for ival in range(2):
        lls = LinkedLineSpec(data={'line': ['i' + str(ival)],
                                   'linked_column': ['b'],
                                   'linked_main_column': ['c'],
                                   'columns': {name: ['d' + str(ival)]},
                                   'expand_at': []})
        cfg.linked_lines.append(lls)


def test_uniq_col_linked_path(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that a repeat between two linked lines names both indexes."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1']}
    _two_linked_lines(cfg, 'b')
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    errmsg = ['Repeated column name(s): b at linked_lines[0].columns[b], '
              'linked_lines[1].columns[b]']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_uniq_col_key_path(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that a repeat of the key column names column_name_for_key."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1'], 'key_col': ['k1']}
    cfg.linked_lines = []
    assert cfg.include_key
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    errmsg = ['Repeated column name(s): key_col at '
              'main_line.columns[key_col], column_name_for_key']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_uniq_col_nested_path(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that validating a subtree prefixes the reported paths."""
    cfg = ExtractConfig()
    cfg.main_line.columns = {'a': ['a1'], 'b': ['b1']}
    _two_linked_lines(cfg, 'b')
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr, member_name='extract')
    errmsg = ['Repeated column name(s): b at '
              'extract.linked_lines[0].columns[b], '
              'extract.linked_lines[1].columns[b], '
              'extract.main_line.columns[b]']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_csv_dialect_validation_ok(capsys: pytest.CaptureFixture[str]) -> None:
    """Test OK case of CSV dialect validation."""
    cfg = ExtractConfig()
    assert cfg.output is not None
    cfg.output.csv = TioJsonCsvConfig(dialect=CsvDialect.UNIX, delimiter=',')
    cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys)


def test_csv_dialect_nok1(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK case 1 of CSV dialect validation."""
    cfg = ExtractConfig()
    assert cfg.output is not None
    cfg.output.csv = TioJsonCsvConfig()
    assert cfg.output.csv is not None
    setattr(cfg.output.csv, 'dialect', 'csv.unix_dialects')
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    errmsg = ['csv.dialect',
              'must be a CsvDialect value or None']
    check_capsys(capsys=capsys, in_err=errmsg)


def test_csv_dialect_nok2(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK case 2 of CSV dialect validation."""
    cfg = ExtractConfig()
    assert cfg.output is not None
    cfg.output.csv = TioJsonCsvConfig(dialect=CsvDialect.UNIX)
    assert cfg.output.csv is not None
    cfg.output.csv.delimiter = '::'
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    errmsgs = ['Value for output.csv.delimiter',
               'length 2',
               'greater than maximum 1']
    check_capsys(capsys=capsys, in_err=errmsgs)


def _line_spec(cfg: ExtractConfig, spec: str) -> LineSpecBase:
    """Return the main line, or the first linked line, of cfg."""
    return cfg.main_line if spec == 'main_line' else cfg.linked_lines[0]


@pytest.mark.parametrize('spec, member, value',
                         [('main_line', 'line', ['ab', 'cd']),
                          ('main_line', 'expand_at', []),
                          ('linked_lines[0]', 'columns',
                           {'Customer name': [], 'Street': ['s'],
                            'Street number': ['n', 'm']}),
                          ('linked_lines[0]', 'linked_main_column',
                           ['xy', 'ab']),
                          ('linked_lines[0]', 'linked_column', []),
                          ('linked_lines[0]', 'expand_at', [['a', 'b'], []]),
                          ('main_line', 'dict_at_line_is_record', True),
                          ('linked_lines[0]', 'dict_at_line_is_record',
                           False)])
def test_line_spec_value_ok(capsys: pytest.CaptureFixture[str], spec: str,
                            member: str, value: object) -> None:
    """Test OK values of the members of the line specifications."""
    cfg = ExtractConfig()
    setattr(_line_spec(cfg, spec), member, value)
    cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('member, prefix', [(None, ''),
                                            ('extract', 'extract.')])
@pytest.mark.parametrize('spec, attr, value, errmsg',
                         [('main_line', 'line', 'str',
                           'Value for {p}.line is not a list'),
                          ('main_line', 'line', [1, 2],
                           'Value 1 for {p}.line at index 0 is not of type '
                           'str'),
                          ('linked_lines[0]', 'line', ['ab', 2],
                           'Value 2 for {p}.line at index 1 is not of type '
                           'str'),
                          ('main_line', 'columns', 2,
                           'Value for {p}.columns is not a dict'),
                          ('linked_lines[0]', 'columns', {3: ['a']},
                           'Key 3 in {p}.columns is not of type str'),
                          ('main_line', 'columns', {'ab': 'cd'},
                           'Value cd for {p}.columns[ab] is not of type '
                           'list'),
                          ('linked_lines[0]', 'columns', {'ab': ['c', 1]},
                           'Value 1 for {p}.columns[ab] at index 1 is not '
                           'of type str'),
                          ('main_line', 'expand_at', ['x'],
                           'Value for {p}.expand_at[0] is not a list'),
                          ('linked_lines[0]', 'expand_at', [['a', 2]],
                           'Value 2 for {p}.expand_at[0] at index 1 is not '
                           'of type str'),
                          ('linked_lines[0]', 'linked_main_column',
                           ['xy', 4], 'Value 4 for {p}.linked_main_column '
                           'at index 1 is not of type str'),
                          ('linked_lines[0]', 'linked_column', 'ab',
                           'Value for {p}.linked_column is not a list'),
                          ('main_line', 'dict_at_line_is_record', 'yes',
                           'Value for {p}.dict_at_line_is_record is not of '
                           'type bool'),
                          ('linked_lines[0]', 'dict_at_line_is_record', 1,
                           'Value for {p}.dict_at_line_is_record is not of '
                           'type bool')])
def test_line_spec_value_nok(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                             member: Optional[str], prefix: str, spec: str,
                             attr: str, value: object, errmsg: str) -> None:
    """Test that a bad member value is refused, naming its whole path."""
    cfg = ExtractConfig()
    setattr(_line_spec(cfg, spec), attr, value)
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr, member_name=member)
    check_capsys(capsys=capsys, in_err=errmsg.format(p=prefix + spec))


@pytest.mark.parametrize('member, value, errmsg',
                         [('main_line', LinkedLineSpec(),
                           'main_line must be MainLineSpec'),
                          ('main_line', 3, 'main_line must be MainLineSpec'),
                          ('linked_lines', LinkedLineSpec(),
                           'linked_lines must be a list'),
                          ('linked_lines', [LinkedLineSpec(), MainLineSpec()],
                           'linked_lines[1] must be LinkedLineSpec'),
                          ('linked_lines', [2],
                           'linked_lines[0] must be LinkedLineSpec')])
def test_line_spec_type_nok(capsys: pytest.CaptureFixture[str], member: str,
                            value: object, errmsg: str) -> None:
    """Test that a line specification of the wrong type is refused."""
    cfg = ExtractConfig()
    setattr(cfg, member, value)
    with pytest.raises(TypeError):
        cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err=errmsg)


@pytest.mark.parametrize('attr',
                         [['What'], ['Street'],
                          ['How many', 'Street number']])
def test_cross_check_attrs_ok(capsys: pytest.CaptureFixture[str],
                              attr: list[str]) -> None:
    """Test OK case of out_xml_attributes reference validation."""
    cfg = ExtractConfig()
    cfg.out_xml_attributes = attr
    cfg.validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('attr, errmsgs',
                         [(['Where'],
                           ['out_xml_attributes includes column "Where"']),
                          (['Road'],
                           ['out_xml_attributes includes column "Road"']),
                          (['How many', 'Street number', 'abc'],
                           ['out_xml_attributes includes column "abc"'])])
def test_cross_check_attrs_nok(capsys: pytest.CaptureFixture[str],
                               attr: list[str], errmsgs: list[str]) -> None:
    """Test not OK case of out_xml_attributes reference validation."""
    cfg = ExtractConfig()
    cfg.out_xml_attributes = attr
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    checkmsg = deepcopy(errmsgs)
    checkmsg.append('but that column is not extracted')
    check_capsys(capsys=capsys, in_err=checkmsg)


def test_extract_cfg_nochange(capsys: pytest.CaptureFixture[str]) -> None:
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    txt = cfg.as_json_string(stderr_file=sys.stderr)
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    check_capsys(capsys=capsys)
