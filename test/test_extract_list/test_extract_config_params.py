#! /usr/local/bin/python3
"""Test parameter data for extract list configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import pytest
from config_as_json import Config
from extract_list.config_enums import FormatRequest, InFileType, \
    MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineSpec, MainLineSpec
from extract_list.output_config import ExtractOutputConfig
from .check_capsys import check_capsys


def test_extract_config_is_config_and_params(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that ExtractConfig combines params and JSON configuration."""
    cfg = ExtractConfig()
    assert isinstance(cfg, ExtractConfigParams)
    assert isinstance(cfg, Config)
    check_capsys(capsys=capsys)


def test_extract_config_params_default_values(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test default values in ExtractConfigParams."""
    params = ExtractConfigParams()
    assert params.infile_type == InFileType.JSON
    assert params.infile_encoding == 'utf-8'
    assert not params.in_xml_strip_at
    assert params.include_key
    assert params.column_name_for_key == 'key col'
    assert params.missing_input_for_column == MissingInputForColumn.EMPTY
    assert isinstance(params.main_line, MainLineSpec)
    assert len(params.linked_lines) == 1
    assert isinstance(params.linked_lines[0], LinkedLineSpec)
    assert params.one_output_line_per_main_line
    assert params.outfile_border == FormatRequest.NO
    assert params.outfile_filtered_area == FormatRequest.NO
    assert isinstance(params.output, ExtractOutputConfig)
    assert params.output.format_name is not None
    assert params.output.format_name.lower() == 'excel'
    assert params.output.character_encoding == 'utf-8'
    assert params.output.implementation is None
    assert params.column_order == ['What', 'How many', 'Customer name',
                                   'Street', 'Street number', 'key col']
    assert not params.order_rows_by
    assert params.out_xml_attributes == ['What']
    check_capsys(capsys=capsys)


def test_extract_config_params_mutable_defaults_are_independent(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that mutable default values are not shared by instances."""
    first = ExtractConfigParams()
    second = ExtractConfigParams()
    first.main_line.columns['Extra'] = ['extra']
    first.linked_lines[0].columns['Linked extra'] = ['linked_extra']
    first.column_order.append('Extra')
    first.order_rows_by.append('What')
    first.out_xml_attributes.append('How many')
    first.output.character_encoding = 'iso8859-1'
    assert 'Extra' not in second.main_line.columns
    assert 'Linked extra' not in second.linked_lines[0].columns
    assert 'Extra' not in second.column_order
    assert not second.order_rows_by
    assert second.out_xml_attributes == ['What']
    assert second.output.character_encoding == 'utf-8'
    check_capsys(capsys=capsys)


def test_encoding_fallback(capsys: pytest.CaptureFixture[str]) -> None:
    """Test output encoding fallback when no encoding is configured."""
    params = ExtractConfigParams()
    params.output.character_encoding = None
    assert params.output_encoding() == 'utf-8'
    check_capsys(capsys=capsys)
