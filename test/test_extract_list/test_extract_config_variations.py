#! /usr/local/bin/python3
"""Test variations of configuration file for extract list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
from json import dumps as json_dumps, loads as json_loads
# from enum import Enum, auto
import sys
import pytest
from config_as_json import ConfigBadJson, InvalidConfiguration, \
    InvalidConfigurationValue
from tableio import CsvDialect
from tableio_cfg_json import TioJsonCsvConfig
from extract_list.config_enums import InFileType, MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import LinkedLineSpec, MainLineSpec
from extract_list.xl_migrate_cfg_warn_hook import XlMigrateCfgWarnHook
from .check_cfgs_equal import check_cfgs_equal
from .check_capsys import check_capsys


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         ['JSON', 'XML', 'CSV', 'Excel', 'txt',
                          'Plaintxt'])
def test_extract_config_var1(capsys: pytest.CaptureFixture[str], inenc: str,
                             infiletype: InFileType, outenc: str,
                             outfiletype: str) -> None:
    """Test variation 1 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.output.format_name = deepcopy(outfiletype)
    cfg.output.character_encoding = deepcopy(outenc)
    if outfiletype.lower() == 'xml':
        cfg.main_line.columns = {'What': ['items', 'item'],
                                 'Quantity': ['items', 'quantity']}
        cfg.linked_lines = []
        cfg.include_key = False
        cfg.column_order = ['What', 'Quantity']
        cfg.out_xml_attributes = ['What']
    cfg.validate(stderr_file=sys.stderr)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.infile_type == infiletype
    assert cf2.infile_encoding == inenc
    assert cf2.output.format_name.lower() == outfiletype.lower()
    assert cf2.output_encoding() == outenc
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('strip', [True, False])
@pytest.mark.parametrize('inck', [True, False])
@pytest.mark.parametrize('miss', [MissingInputForColumn.EMPTY,
                                  MissingInputForColumn.ERROR])
@pytest.mark.parametrize('attr', [['Street'], ['How many'],
                                  ['Street', 'How many']])
def test_extract_config_var2(capsys: pytest.CaptureFixture[str], strip: bool,
                             inck: bool, miss: MissingInputForColumn,
                             attr: list[str]) -> None:
    """Test variation 2 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.in_xml_strip_at = deepcopy(strip)
    cfg.include_key = deepcopy(inck)
    cfg.missing_input_for_column = deepcopy(miss)
    cfg.out_xml_attributes = deepcopy(attr)
    if not inck:
        cfg.column_order.remove('key col')
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.in_xml_strip_at == strip
    assert cf2.include_key == inck
    assert cf2.missing_input_for_column == miss
    assert cf2.out_xml_attributes == attr
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('coname', ['abc', 'key column'])
@pytest.mark.parametrize('csv_dialect', [CsvDialect.EXCEL, CsvDialect.UNIX])
@pytest.mark.parametrize('deli', [',', ';', ' '])
@pytest.mark.parametrize('excl', ['OpenPyXL', 'pylightxl', 'XlsxWriter'])
def test_extract_config_var3(capsys: pytest.CaptureFixture[str], coname: str,
                             csv_dialect: CsvDialect, deli: str,
                             excl: str) -> None:
    """Test variation 3 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.column_name_for_key = deepcopy(coname)
    assert cfg.output is not None
    cfg.output.csv = TioJsonCsvConfig(dialect=deepcopy(csv_dialect),
                                      delimiter=deepcopy(deli))
    cfg.output.implementation = deepcopy(excl)
    cfg.column_order.remove('key col')
    cfg.column_order.append(deepcopy(coname))
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.column_name_for_key == coname
    assert cf2.output is not None
    assert cf2.output.csv is not None
    assert cf2.output.csv.dialect == csv_dialect
    assert cf2.output.csv.delimiter == deli
    assert cf2.output.implementation == excl
    check_capsys(capsys=capsys)


ml1 = deepcopy(ExtractConfig.example_main_line())
ml1.columns['Box'] = ['box', 'number']
ll1 = deepcopy(ExtractConfig.example_linked_line())
ll1.columns['Zip'] = ['address', 'zip']
kord1 = ['What', 'How many', 'Customer name',
         'Street', 'Street number', 'key col',
         'Box', 'Zip']
ml2 = deepcopy(ExtractConfig.example_main_line())
del ml2.columns['How many']
ll2 = deepcopy(ExtractConfig.example_linked_line())
del ll2.columns['Street number']
kord2 = ['What', 'Customer name', 'Street', 'key col']


@pytest.mark.parametrize('main,linked,order',
                         [(ml1, ll1, kord1), (ml2, ll2, kord2)])
def test_extract_config_var4(capsys: pytest.CaptureFixture[str],
                             main: MainLineSpec, linked: LinkedLineSpec,
                             order: list[str]) -> None:
    """Test variation 4 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.main_line = deepcopy(main)
    cfg.linked_lines = deepcopy([linked])
    cfg.column_order = deepcopy(order)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.main_line.columns == main.columns
    assert cf2.main_line.line == main.line
    assert len(cf2.linked_lines) == 1
    assert cf2.linked_lines[0].columns == linked.columns
    assert cf2.linked_lines[0].line == linked.line
    assert cf2.linked_lines[0].linked_column == linked.linked_column
    assert cf2.linked_lines[0].linked_main_column == linked.linked_main_column
    assert cf2.column_order == order
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ord_row', [['How many', 'What'],
                                     ['Street']])
@pytest.mark.parametrize('one', [True, False])
def test_extract_config_var5(capsys: pytest.CaptureFixture[str], one: bool,
                             ord_row: list[str]) -> None:
    """Test variation 5 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.one_output_line_per_main_line = deepcopy(one)
    cfg.order_rows_by = deepcopy(ord_row)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.one_output_line_per_main_line == one
    assert cf2.order_rows_by == ord_row
    assert cfg.get_order_rows_by() == ord_row
    check_capsys(capsys=capsys)


def _set_config_value(config: ExtractConfig, member_path: str,
                      value: object) -> None:
    """Set a test value on a possibly nested configuration member."""
    if member_path == 'output.csv':
        assert config.output is not None
        setattr(config.output, 'csv', value)
        return
    if member_path.startswith('output.'):
        assert config.output is not None
        setattr(config.output, member_path.removeprefix('output.'), value)
        return
    setattr(config, member_path, value)


@pytest.mark.parametrize('attr,val,exc, msgs',
                         [('infile_type', 15, InvalidConfiguration,
                           ['Value for infile_type',
                            'is not of type InFileType']),
                          ('infile_type', '15', InvalidConfiguration,
                           ['Value for infile_type',
                            'is not of type InFileType']),
                          ('infile_encoding', 'abc', InvalidConfiguration,
                           ['abc is not a recognized character encoding']),
                          ('include_key', 15, InvalidConfiguration,
                           ['Value for include_key',
                            'is not of type bool']),
                          ('column_name_for_key', 15, InvalidConfiguration,
                           ['Value for column_name_for_key',
                            'is not of type str']),
                          ('missing_input_for_column', 'no',
                           InvalidConfiguration,
                           ['Value for missing_input_for_column',
                            'is not of type MissingInputForColumn']),
                          ('output.format_name', 'line',
                           InvalidConfigurationValue,
                           ['Value line for format_name',
                            'CSV, Excel']),
                          ('output.character_encoding', 'def',
                           InvalidConfiguration,
                           ['def is not a recognized character encoding']),
                          ('output.implementation', 'lib',
                           InvalidConfigurationValue,
                           ['Value lib for implementation',
                            'OpenPyXL, XlsxWriter',
                            'csv, mformat, odfdo, pylightxl']),
                          ('column_order', 'ordered', InvalidConfiguration,
                           ['Value for column_order is not a list.']),
                          ('column_order', [7], InvalidConfiguration,
                           ['Value 7 for column_order at index 0',
                            'is not of type str.']),
                          ('column_order', ['What'], SystemExit,
                           ['Extracted column "Customer name" is missing']),
                          ('column_order',
                           ['What', 'How many', 'Customer name',
                            'Street', 'Street number', 'key col', 'abc'],
                           SystemExit,
                           ['column order includes column "abc"',
                            'but that column is not extracted']),
                          ('column_order',
                           ['What', 'How many', 'What', 'Customer name',
                            'Street', 'Street number', 'key col'],
                           InvalidConfiguration,
                           ['Value What for column_order at index 2',
                            'duplicates the value at index 0.']),
                          ('out_xml_attributes', 'What',
                           InvalidConfiguration,
                           'Value for out_xml_attributes is not a list.'),
                          ('out_xml_attributes', ['nothing'], SystemExit,
                           ['Attribute name "nothing" in out_xml_attributes',
                            'but no column with that name extracted']),
                          ('output.csv', 'dial', TypeError,
                           ['Nested Config member csv',
                            'must be TioJsonCsvConfig']),
                          ('order_rows_by', ['Whatt'], SystemExit,
                           ['order rows by includes column "Whatt"',
                            'but that column is not extracted']),
                          ('order_rows_by', 'What', InvalidConfiguration,
                           'Value for order_rows_by is not a list.'),
                          ('order_rows_by', [7], InvalidConfiguration,
                           ['Value 7 for order_rows_by at index 0',
                            'is not of type str.'])])
def test_extract_config_err1(capsys: pytest.CaptureFixture[str], attr: str,
                             val: object, exc: type[BaseException],
                             msgs: str | list[str]) -> None:
    """Test not OK variations 1 of ExtractConfig."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    _set_config_value(config=cfg, member_path=attr, value=val)
    with pytest.raises(exc):
        txt = cfg.as_json_string(stderr_file=sys.stderr)
        _ = ExtractConfig(from_json_data_text=txt, stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err=msgs)


def test_extract_config_bad_json_enum_name(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that enum JSON text is checked by Config parsing."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    data = json_loads(cfg.as_json_string(stderr_file=sys.stderr))
    data['infile_type'] = '15'
    with pytest.raises(ConfigBadJson):
        _ = ExtractConfig(from_json_data_text=json_dumps(data),
                          stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err='15 is not one of: JSON, XML')


def test_extract_config_old_excel_library_is_ignored(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that old outfile_excel_library values are ignored."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    data = json_loads(cfg.as_json_string(stderr_file=sys.stderr))
    data['outfile_excel_library'] = 'lib'
    cf2 = ExtractConfig(from_json_data_text=json_dumps(data),
                        stderr_file=sys.stderr,
                        auto_ch_hook=XlMigrateCfgWarnHook())
    assert cf2.output.implementation is None
    assert not hasattr(cf2, 'outfile_excel_library')
    check_capsys(capsys=capsys, in_err='migrate-cfg')


def test_old_tableio_output_keys_are_migrated(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that old TableIO output keys are read as nested output."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    data = json_loads(cfg.as_json_string(stderr_file=sys.stderr))
    del data['output']
    data['outfile_type'] = 'CSV'
    data['outfile_encoding'] = 'iso8859-1'
    data['outfile_excel_library'] = 'PYLIGHTXL'
    data['out_csv_dialect'] = {
        'name': 'csv.excel_tab',
        'delimiter': None,
        'quoting': 'csv.quote_minimal'}
    cf2 = ExtractConfig(from_json_data_text=json_dumps(data),
                        stderr_file=sys.stderr,
                        auto_ch_hook=XlMigrateCfgWarnHook())
    assert cf2.output.format_name == 'CSV'
    assert cf2.output.character_encoding == 'iso8859-1'
    assert cf2.output.implementation is None
    assert cf2.output.csv is not None
    assert cf2.output.csv.dialect == CsvDialect.EXCEL
    assert cf2.output.csv.delimiter == '\t'
    assert cf2.output.csv.quoting == 'minimal'
    check_capsys(capsys=capsys, in_err='migrate-cfg')


@pytest.mark.parametrize('old_format, new_format',
                         [('JSON', 'JSON'), ('XML', 'XML'),
                          ('TXT', 'Plaintxt')])
def test_old_0214_formats(capsys: pytest.CaptureFixture[str], old_format: str,
                          new_format: str) -> None:
    """Test that old 0.2.14 internal formats become current output."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    if old_format == 'XML':
        cfg.main_line.columns = {'What': ['items', 'item'],
                                 'Quantity': ['items', 'quantity']}
        cfg.linked_lines = []
        cfg.include_key = False
        cfg.column_order = ['What', 'Quantity']
    data = json_loads(cfg.as_json_string(stderr_file=sys.stderr))
    del data['output']
    data['outfile_type'] = old_format
    data['outfile_encoding'] = 'iso8859-1'
    data['outfile_excel_library'] = 'PYLIGHTXL'
    cf2 = ExtractConfig(from_json_data_text=json_dumps(data),
                        stderr_file=sys.stderr,
                        auto_ch_hook=XlMigrateCfgWarnHook())
    assert cf2.output.format_name == new_format
    assert cf2.output.character_encoding == 'iso8859-1'
    check_capsys(capsys=capsys, in_err='migrate-cfg')


def test_current_output_wins_over_old_keys(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that current output config wins when old output keys exist."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    assert cfg.output is not None
    cfg.output.format_name = 'CSV'
    data = json_loads(cfg.as_json_string(stderr_file=sys.stderr))
    data['outfile_type'] = 'JSON'
    data['outfile_encoding'] = 'iso8859-1'
    cf2 = ExtractConfig(from_json_data_text=json_dumps(data),
                        stderr_file=sys.stderr)
    assert cf2.output.format_name == 'CSV'
    assert cf2.output.character_encoding == 'utf-8'
    msgs = ['Both new config parameter output[format_name]',
            'Ignoring old parameter outfile_type',
            'Both new config parameter output[character_encoding]',
            'Ignoring old parameter outfile_encoding']
    check_capsys(capsys=capsys, in_err=msgs)


def test_extract_config_err2(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK variation 2 of ExtractConfig."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    cfg.main_line.columns['Cost'] = ['item info', 'cost']
    txt = cfg.as_json_string(stderr_file=sys.stderr)
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt, stderr_file=sys.stderr)
    check_capsys(capsys=capsys,
                 in_err='Extracted column "Cost" is missing in column_order')


def test_extract_config_err3(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK variation 3 of ExtractConfig."""
    cfg = ExtractConfig(stderr_file=sys.stderr)
    cfg.linked_lines[0].columns['Zip'] = ['zip']
    txt = cfg.as_json_string(stderr_file=sys.stderr)
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt, stderr_file=sys.stderr)
    check_capsys(capsys=capsys,
                 in_err='Extracted column "Zip" is missing in column_order')


def test_extract_config_err4(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK variation 4 of ExtractConfig."""
    cfg = ExtractConfig()
    cfg.column_order.append('Zip')
    txt = cfg.as_json_string(stderr_file=sys.stderr)
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt, stderr_file=sys.stderr)
    msgs = ['column order includes column "Zip"',
            'but that column is not extracted']
    check_capsys(capsys=capsys, in_err=msgs)


def test_xml_column_names_nok(capsys: pytest.CaptureFixture[str]) -> None:
    """Test not OK XML column name validation."""
    cfg = ExtractConfig()
    cfg.output.format_name = 'XML'
    with pytest.raises(InvalidConfiguration):
        cfg.validate(stderr_file=sys.stderr)
    msgs = ['XML output column names in column_order',
            'must not contain whitespace', 'How many', 'Customer name',
            'Street number', 'key col']
    check_capsys(capsys=capsys, in_err=msgs)
