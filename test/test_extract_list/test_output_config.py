#! /usr/local/bin/python3
"""Test unified output configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional
import sys
import pytest
from tableio import FileAccess
from extract_list.config_enums import get_outfile_capabilities
from extract_list.extract_config import ExtractConfig
from extract_list.output_config import ExtractOutputConfig
from .bogus_cfg import cfg_text_without
from .check_capsys import check_capsys


@pytest.mark.parametrize('format_name, expected_name',
                         [('json', 'JSON'),
                          ('XML', 'XML'),
                          ('plaintxt', 'Plaintxt')])
@pytest.mark.parametrize('implementation, expected_impl',
                         [(None, None),
                          ('INTERNAL', 'internal')])
def test_internal_output_init(capsys: pytest.CaptureFixture[str],
                              format_name: str, expected_name: str,
                              implementation: Optional[str],
                              expected_impl: Optional[str]) -> None:
    """Test direct construction of internal output configurations."""
    cfg = ExtractOutputConfig(capabilities=get_outfile_capabilities(),
                              file_access=FileAccess.CREATE,
                              format_name=format_name,
                              implementation=implementation,
                              allowed_formats=['CSV', expected_name])
    assert cfg.format_name == expected_name
    assert cfg.implementation == expected_impl
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('format_name', [None, 'Excel', 'CSV', 'JSON',
                                         'Plaintxt'])
def test_output_utf8_default(capsys: pytest.CaptureFixture[str],
                             format_name: Optional[str]) -> None:
    """Test that the default character encoding is utf-8 for every format."""
    cfg = ExtractOutputConfig(capabilities=get_outfile_capabilities(),
                              file_access=FileAccess.CREATE,
                              format_name=format_name, stderr_file=sys.stderr)
    default_output = ExtractConfig(stderr_file=sys.stderr).output
    assert cfg.character_encoding == 'utf-8'
    assert default_output.character_encoding == 'utf-8'
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ok_to_use_defaults', [False, True])
def test_output_no_encoding(capsys: pytest.CaptureFixture[str],
                            ok_to_use_defaults: bool) -> None:
    """Test that JSON data without an encoding gives None, meaning utf-8."""
    text = cfg_text_without(('output', 'character_encoding'))
    cfg = ExtractConfig(from_json_data_text=text, stderr_file=sys.stderr,
                        ok_to_use_defaults=ok_to_use_defaults)
    assert cfg.output.character_encoding is None
    assert cfg.output_encoding() == 'utf-8'
    assert not cfg.kept_value_paths()
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('format_name, expected_name',
                         [(None, 'Excel'), ('CSV', 'CSV'), ('JSON', 'JSON'),
                          ('Plaintxt', 'Plaintxt')])
def test_output_all_options(capsys: pytest.CaptureFixture[str],
                            format_name: Optional[str],
                            expected_name: str) -> None:
    """Test settings with all options, where TableIO gives the encoding.

    The encoding TableIO gives is kept, and the options of other formats,
    such as the CSV section, are included too.
    """
    cfg = ExtractOutputConfig(capabilities=get_outfile_capabilities(),
                              file_access=FileAccess.CREATE,
                              format_name=format_name,
                              include_all_options=True, stderr_file=sys.stderr)
    assert cfg.format_name == expected_name
    assert cfg.character_encoding == 'utf-8'
    assert cfg.csv is not None
    check_capsys(capsys=capsys)
