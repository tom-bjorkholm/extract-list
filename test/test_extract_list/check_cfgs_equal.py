#! /usr/local/bin/python3
"""Check that two configurations for extract list are equal."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License


from json import loads as json_loads
from typing import Optional, cast
import sys
from tableio_cfg_json import TioJsonConfig
from extract_list.extract_config import ExtractConfig


def _output_json(
        output: Optional[TioJsonConfig]) -> Optional[dict[str, object]]:
    """Get JSON-compatible data from an optional output config."""
    if output is None:
        return None
    return cast(dict[str, object],
                json_loads(output.as_json_string(stderr_file=sys.stderr)))


def check_cfgs_equal(cf1: ExtractConfig, cf2: ExtractConfig) -> None:
    """Check that two configurations for extract list are equal."""
    assert cf1.infile_type == cf2.infile_type
    assert cf1.infile_encoding == cf2.infile_encoding
    assert cf1.in_xml_strip_at == cf2.in_xml_strip_at
    assert cf1.include_key == cf2.include_key
    assert cf1.column_name_for_key == cf2.column_name_for_key
    assert cf1.missing_input_for_column == cf2.missing_input_for_column
    assert cf1.main_line.line == cf2.main_line.line
    assert cf1.main_line.columns == cf2.main_line.columns
    assert len(cf1.linked_lines) == len(cf2.linked_lines)
    for elem1, elem2 in zip(cf1.linked_lines, cf2.linked_lines):
        assert elem1.line == elem2.line
    assert cf1.one_output_line_per_main_line == \
        cf2.one_output_line_per_main_line
    assert _output_json(cf1.output) == _output_json(cf2.output)
    assert cf1.internal_output_format == cf2.internal_output_format
    assert cf1.internal_output_encoding == cf2.internal_output_encoding
    assert cf1.column_order == cf2.column_order
    assert cf1.out_xml_attributes == cf2.out_xml_attributes
