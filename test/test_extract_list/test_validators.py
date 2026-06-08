#! /usr/local/bin/python3
"""Test extract-list configuration validators."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import cast
import sys
import pytest
from config_as_json import Config, InvalidConfiguration
from extract_list.validators import ExtractedColumnNameValidator, \
    _column_names_from_spec
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


@pytest.mark.parametrize('spec, msgs',
                         [({'line': []},
                           ['Line specification must contain a columns dict']),
                          ({'columns': {3: ['value']}},
                           ['Extracted column name 3 is not a string']),
                          (7,
                           ['Line specification has unexpected type int'])])
def test_col_spec_errors(capsys: pytest.CaptureFixture[str], spec: object,
                         msgs: list[str]) -> None:
    """Test invalid line specification shapes for column name extraction."""
    with pytest.raises(InvalidConfiguration):
        _column_names_from_spec(spec=spec, stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err=msgs)
