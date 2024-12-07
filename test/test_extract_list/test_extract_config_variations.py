#! /usr/local/bin/python3
"""Test variations of configuration file for extract list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from copy import deepcopy
# from enum import Enum, auto
import pytest
from check_cfgs_equal import check_cfgs_equal
from excel_list_transform.config_enums import ExcelLib
from excel_list_transform.config import ConfigBadJson
from extract_list.config_enums import InFileType, OutFileType, \
    MissingInputForColumn
from extract_list.extract_config import ExtractConfig


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         [OutFileType.JSON, OutFileType.XML, OutFileType.CSV,
                          OutFileType.EXCEL, OutFileType.TXT])
def test_extract_config_var1(capsys, inenc, infiletype, outenc, outfiletype):
    """Test variation 1 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.outfile_encoding = deepcopy(outenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.outfile_type = deepcopy(outfiletype)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.infile_type == infiletype
    assert cf2.infile_encoding == inenc
    assert cf2.outfile_type == outfiletype
    assert cf2.outfile_encoding == outenc
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('strip', [True, False])
@pytest.mark.parametrize('inck', [True, False])
@pytest.mark.parametrize('miss', [MissingInputForColumn.EMPTY,
                                  MissingInputForColumn.ERROR])
@pytest.mark.parametrize('attr', [['Street'], ['How many'],
                                  ['Street', 'How many']])
def test_extract_config_var2(capsys, strip, inck, miss, attr):
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
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('coname', ['abc', 'key column'])
@pytest.mark.parametrize('csname', ['csv.excel', 'csv.unix_dialect'])
@pytest.mark.parametrize('deli', [',', ';', ' '])
@pytest.mark.parametrize('excl', [ExcelLib.OPENPYXL, ExcelLib.PYLIGHTXL,
                                  ExcelLib.XLSXWRITER])
def test_extract_config_var3(capsys, coname, csname, deli, excl):
    """Test variation 3 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.column_name_for_key = deepcopy(coname)
    cfg.out_csv_dialect['name'] = deepcopy(csname)
    cfg.out_csv_dialect['delimiter'] = deepcopy(deli)
    cfg.outfile_excel_library = deepcopy(excl)
    cfg.column_order.remove('key col')
    cfg.column_order.append(deepcopy(coname))
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.column_name_for_key == coname
    assert cf2.out_csv_dialect['name'] == csname
    assert cf2.out_csv_dialect['delimiter'] == deli
    assert cf2.outfile_excel_library == excl
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


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
def test_extract_config_var4(capsys, main, linked, order):
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
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('one', [True, False])
def test_extract_config_var5(capsys, one):
    """Test variation 5 of configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.one_output_line_per_main_line = deepcopy(one)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.one_output_line_per_main_line == one
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('attr,val,exc, msgs',
                         [('infile_type', 15, ConfigBadJson,
                           ['int not str as expected']),
                          ('infile_type', '15', ConfigBadJson,
                           ['15 is not one of: JSON, XML']),
                          ('infile_encoding', 'abc', SystemExit,
                           ['abc is not a recognized encoding']),
                          ('include_key', 15, SystemExit,
                           ['Configuration parameter "include_key" has wrong',
                            'Type is "int", but expected type "bool"']),
                          ('column_name_for_key', 15, SystemExit,
                           ['Type is "int", but expected type "str"']),
                          ('missing_input_for_column', 'no', ConfigBadJson,
                           ['no is not one of: ERROR, EMPTY']),
                          ('outfile_type', 'line', ConfigBadJson,
                           ['line is not one of: EXCEL, CSV, JSON, XML, TXT']),
                          ('outfile_encoding', 'def', SystemExit,
                           ['def is not a recognized encoding']),
                          ('outfile_excel_library', 'lib', ConfigBadJson,
                           ['lib is not one of: OPENPYXL, XLSXWRITER,',
                            'OPENPYXL, XLSXWRITER, PYLIGHTXL']),
                          ('column_order', 'ordered', SystemExit,
                           ['Type is "str", but expected type "list".']),
                          ('column_order', ['What'], SystemExit,
                           ['Extracted column "Customer name" is missing']),
                          ('column_order',
                           ['What', 'How many', 'Customer name',
                            'Street', 'Street number', 'key col', 'abc'],
                           SystemExit,
                           ['column order includes column "abc"',
                            'but that column is not extracted']),
                          ('out_xml_attributes', 'What', SystemExit,
                           ['"out_xml_attributes" has wrong type.',
                            'Type is "str", but expected type "list"']),
                          ('out_xml_attributes', ['nothing'], SystemExit,
                           ['Attribute name "nothing" in out_xml_attributes',
                            'but no column with that name extracted']),
                          ('out_csv_dialect', 'dial', KeyError,
                           'Not dictionary for out_csv_dialect')])
def test_extract_config_err1(capsys, attr, val, exc, msgs):
    """Test not OK variations 1 of ExtractConfig."""
    cfg = ExtractConfig()
    setattr(cfg, attr, val)
    txt = cfg.as_json_string()
    with pytest.raises(exc):
        _ = ExtractConfig(from_json_data_text=txt)
    out, err = capsys.readouterr()
    assert '' == out
    for errmsg in msgs:
        assert errmsg in err


def test_extract_config_err2(capsys):
    """Test not OK variation 2 of ExtractConfig."""
    cfg = ExtractConfig()
    cfg.main_line.columns['Cost'] = ['item info', 'cost']
    txt = cfg.as_json_string()
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt)
    out, err = capsys.readouterr()
    assert '' == out
    assert 'Extracted column "Cost" is missing in column_order' in err


def test_extract_config_err3(capsys):
    """Test not OK variation 3 of ExtractConfig."""
    cfg = ExtractConfig()
    cfg.linked_lines[0].columns['Zip'] = ['zip']
    txt = cfg.as_json_string()
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt)
    out, err = capsys.readouterr()
    assert '' == out
    assert 'Extracted column "Zip" is missing in column_order' in err


def test_extract_config_err4(capsys):
    """Test not OK variation 4 of ExtractConfig."""
    cfg = ExtractConfig()
    cfg.column_order.append('Zip')
    txt = cfg.as_json_string()
    with pytest.raises(SystemExit):
        _ = ExtractConfig(from_json_data_text=txt)
    out, err = capsys.readouterr()
    assert '' == out
    assert 'column order includes column "Zip"' in err
    assert 'but that column is not extracted' in err
