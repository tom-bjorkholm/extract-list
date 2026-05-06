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
from extract_list.config_enums import InFileType, MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import LinkedLineSpec, MainLineSpec
from .check_cfgs_equal import check_cfgs_equal
from .check_capsys import check_capsys


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         ['JSON', 'XML', 'CSV', 'Excel', 'txt'])
def test_extract_config_var1(capsys: pytest.CaptureFixture[str], inenc: str,
                             infiletype: InFileType, outenc: str,
                             outfiletype: str) -> None:
    """Test variation 1 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.outfile_encoding = deepcopy(outenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.outfile_type = deepcopy(outfiletype)
    cfg.validate(stderr_file=sys.stderr)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.infile_type == infiletype
    assert cf2.infile_encoding == inenc
    assert cf2.outfile_type == outfiletype
    assert cf2.outfile_encoding == outenc
    xmlerr = ['Warning: Column name ',
              'is not a valid column name in XML,',
              'contains white space.']
    errs = None if outfiletype.lower() != 'xml' else xmlerr
    check_capsys(capsys=capsys, in_err=errs)


@pytest.mark.parametrize('strip', [True, False])
@pytest.mark.parametrize('inck', [True, False])
@pytest.mark.parametrize('miss', [MissingInputForColumn.EMPTY,
                                  MissingInputForColumn.ERROR])
@pytest.mark.parametrize('attr', [['Street'], ['How many'],
                                  ['Street', 'How many']])
def test_extract_config_var2(capsys: pytest.CaptureFixture[str],
                             strip: bool, inck: bool,
                             miss: MissingInputForColumn,
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
@pytest.mark.parametrize('csname', ['csv.excel', 'csv.unix_dialect'])
@pytest.mark.parametrize('deli', [',', ';', ' '])
@pytest.mark.parametrize('excl', ['OpenPyXL', 'pylightxl', 'XlsxWriter'])
def test_extract_config_var3(capsys: pytest.CaptureFixture[str],
                             coname: str, csname: str, deli: str,
                             excl: str) -> None:
    """Test variation 3 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.column_name_for_key = deepcopy(coname)
    cfg.out_csv_dialect['name'] = deepcopy(csname)
    cfg.out_csv_dialect['delimiter'] = deepcopy(deli)
    cfg.outfile_implementation = deepcopy(excl)
    cfg.column_order.remove('key col')
    cfg.column_order.append(deepcopy(coname))
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.column_name_for_key == coname
    assert cf2.out_csv_dialect['name'] == csname
    assert cf2.out_csv_dialect['delimiter'] == deli
    assert cf2.outfile_implementation == excl
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
def test_extract_config_var5(capsys: pytest.CaptureFixture[str],
                             one: bool, ord_row: list[str]) -> None:
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
                          ('outfile_type', 'line', InvalidConfigurationValue,
                           ['Value line for outfile_type',
                            'CSV, Excel']),
                          ('outfile_encoding', 'def', InvalidConfiguration,
                           ['def is not a recognized character encoding']),
                          ('outfile_implementation', 'lib',
                           InvalidConfigurationValue,
                           ['Value lib for outfile_implementation',
                            'OpenPyXL, XlsxWriter, pylightxl']),
                          ('column_order', 'ordered', InvalidConfiguration,
                           ['Value for column_order is not a list.']),
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
                          ('out_csv_dialect', 'dial', KeyError,
                           'Not dictionary for out_csv_dialect'),
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
    setattr(cfg, attr, val)
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
                        stderr_file=sys.stderr)
    assert cf2.outfile_implementation is None
    assert not hasattr(cf2, 'outfile_excel_library')
    check_capsys(capsys=capsys)


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
