#! /usr/local/bin/python3
"""Test validators for extract-list configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional
import sys
import pytest
from config_as_json import InvalidConfiguration, InvalidConfigurationValue
from extract_list.config_enums import FormatRequest
from extract_list.extract_config import ExtractConfig
import extract_list.validators as validators_module
from extract_list.validators import OutputImplementationMemberValidator, \
    OutputImplementationValidator
from .check_capsys import check_capsys


def _empty_implementations(format_name: Optional[str],
                           border: FormatRequest,
                           filtered_area: FormatRequest) -> list[str]:
    """Return no implementations for validator error-path tests."""
    _ = format_name
    _ = border
    _ = filtered_area
    return []


def test_output_implementation_member_validator_accepts_none(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that optional output implementation may be None."""
    cfg = ExtractConfig()
    validator = OutputImplementationMemberValidator()
    result = validator.validate_member(config=cfg,
                                       member_name='outfile_implementation',
                                       member_value=None,
                                       stderr_file=sys.stderr)
    assert result is None
    check_capsys(capsys=capsys)


def test_output_implementation_member_validator_clears_internal_format(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that internal output formats ignore implementation values."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'JSON'
    validator = OutputImplementationMemberValidator()
    result = validator.validate_member(config=cfg,
                                       member_name='outfile_implementation',
                                       member_value='OpenPyXL',
                                       stderr_file=sys.stderr)
    assert result is None
    check_capsys(capsys=capsys)


def test_output_implementation_member_validator_normalizes_name(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test normalization of configured output implementation."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'Excel'
    validator = OutputImplementationMemberValidator()
    result = validator.validate_member(config=cfg,
                                       member_name='outfile_implementation',
                                       member_value='openpyxl',
                                       stderr_file=sys.stderr)
    assert result == 'OpenPyXL'
    check_capsys(capsys=capsys)


def test_output_implementation_member_validator_rejects_unknown_name(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test rejection of an unknown output implementation."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'Excel'
    validator = OutputImplementationMemberValidator()
    with pytest.raises(InvalidConfigurationValue):
        validator.validate_member(config=cfg,
                                  member_name='outfile_implementation',
                                  member_value='not an implementation',
                                  stderr_file=sys.stderr)
    check_capsys(capsys=capsys,
                 in_err='Value not an implementation for')


def test_output_implementation_validator_clears_internal_format(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that whole-config validation clears internal implementations."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'XML'
    cfg.outfile_implementation = 'OpenPyXL'
    OutputImplementationValidator().validate(config=cfg,
                                             stderr_file=sys.stderr)
    assert cfg.outfile_implementation is None
    check_capsys(capsys=capsys)


def test_output_implementation_validator_accepts_external_format(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that whole-config validation accepts implemented formats."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'Excel'
    cfg.outfile_implementation = 'OpenPyXL'
    OutputImplementationValidator().validate(config=cfg,
                                             stderr_file=sys.stderr)
    assert cfg.outfile_implementation == 'OpenPyXL'
    check_capsys(capsys=capsys)


def test_output_implementation_validator_rejects_missing_implementation(
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that formats without implementation are rejected."""
    cfg = ExtractConfig()
    cfg.outfile_type = 'Excel'
    monkeypatch.setattr(validators_module, 'list_out_format_implementations',
                        _empty_implementations)
    with pytest.raises(InvalidConfiguration):
        OutputImplementationValidator().validate(config=cfg,
                                                 stderr_file=sys.stderr)
    check_capsys(capsys=capsys,
                 in_err='No implementation can write Excel.')
