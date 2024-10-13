#! /usr/local/bin/python3
"""Test printing list of dicts as JSON and as XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

# import sys
# from tempfile import TemporaryDirectory
from copy import deepcopy
import pytest
from extract_list.extract_config import ExtractConfig


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


# TODO test variations of valid configuraitons
@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
def test_extract_config_var1(capsys, inenc):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
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
    assert cfg.outfile_type == cf2.outfile_type
    assert cfg.outfile_encoding == cf2.outfile_encoding
    assert cfg.outfile_excel_library == cf2.outfile_excel_library
    assert cfg.column_order == cf2.column_order
    assert cfg.out_xml_attributes == cf2.out_xml_attributes
    assert cfg.out_csv_dialect == cf2.out_csv_dialect
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


# TODO test messages for variations of invalid configurations
