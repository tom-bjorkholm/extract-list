#! /usr/local/bin/python3
"""Test unified output configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional
import pytest
from tableio import FileAccess
from extract_list.config_enums import get_outfile_capabilities
from extract_list.output_config import ExtractOutputConfig
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
