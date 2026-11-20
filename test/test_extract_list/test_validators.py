#! /usr/local/bin/python3
"""Test extract-list configuration validators."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import cast
import sys
import pytest
from config_as_json import Config, InvalidConfiguration
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import MainLineSpec
from extract_list.validators import ExtractedColumnNameValidator, XML_NAME
from .check_capsys import check_capsys


def test_validator_cfg_type(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that validators reject non extract-list configuration objects."""
    validator = ExtractedColumnNameValidator()
    bad_config = cast(Config, object())
    with pytest.raises(InvalidConfiguration):
        validator.validate(config=bad_config, stderr_file=sys.stderr)
    msgs = ['Invalid configuration',
            'Expected ExtractConfigParams compatible config']
    check_capsys(capsys=capsys, in_err=msgs)


@pytest.mark.parametrize('name, valid', [
    ('a', True), ('_x', True), ('Kund-nr.2', True), ('åäö', True),
    ('x1', True), ('key_col', True), ('', False), ('1st', False),
    ('123', False), ('-a', False), ('.a', False), ('a b', False),
    ('a\tb', False), ('a/b', False), ('a=b', False), ('"q"', False),
    ("'q'", False), ('a:b', False), ('?x', False), ('!x', False),
    ('<x>', False)])
def test_xml_name(capsys: pytest.CaptureFixture[str], name: str,
                  valid: bool) -> None:
    """Test which column names XML_NAME accepts as XML names."""
    assert bool(XML_NAME.fullmatch(name)) == valid
    check_capsys(capsys=capsys)


def one_column_cfg(name: str, format_name: str) -> ExtractConfig:
    """Return a configuration with one extracted column, called name."""
    cfg = ExtractConfig()
    cfg.output.format_name = format_name
    cfg.main_line = MainLineSpec(data={'line': ['l'], 'columns': {name: ['x']},
                                       'expand_at': []})
    cfg.linked_lines = []
    cfg.include_key = False
    cfg.column_order = [name]
    cfg.order_rows_by = []
    cfg.out_xml_attributes = []
    return cfg


@pytest.mark.parametrize('name, format_name', [
    ('Kund-nr', 'XML'), ('_1', 'XML'), ('1st', 'JSON'), ('a b', 'CSV')])
def test_xml_column_name_ok(capsys: pytest.CaptureFixture[str], name: str,
                            format_name: str) -> None:
    """Test that only XML output requires columns to have XML names."""
    one_column_cfg(name, format_name).validate(stderr_file=sys.stderr)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('name', ['1st', 'a/b', 'a=b', 'a b'])
def test_xml_column_name_nok(capsys: pytest.CaptureFixture[str],
                             name: str) -> None:
    """Test that XML output rejects a column name that is no XML name."""
    with pytest.raises(InvalidConfiguration):
        one_column_cfg(name, 'XML').validate(stderr_file=sys.stderr)
    msgs = ['XML output column names in column_order must be XML names',
            f'Invalid column name(s): {name}']
    check_capsys(capsys=capsys, in_err=msgs)
