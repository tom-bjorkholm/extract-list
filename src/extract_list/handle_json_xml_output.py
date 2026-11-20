#! /usr/local/bin/python3
"""Print list of dicts as JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
import json
import xmltodict
from config_as_json import JsonType
from extract_list.commontypes import Data, Row, Value
from extract_list.extract_config import ExtractConfig


def json_output(data: Data | JsonType, filename: str, encoding: str) -> None:
    """Print list of dicts to JSON."""
    with open(file=filename, mode='w', encoding=encoding) as file:
        json.dump(data, fp=file, indent=2)


def append_to_key(row: Row, key: str, prefix: str) -> None:
    """Add prefix to key in dict row."""
    value: Value = row.pop(key)
    row[prefix + key] = value


def handle_xml_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Handle output to XML file.

    Each row is written as one <row> element in the <data> root element,
    in order, so rows with equal values are all kept. The columns in
    cfg.out_xml_attributes are attributes of <row>, and the other columns,
    the key column included, are elements in it.
    """
    rows = deepcopy(data)
    for row in rows:
        for key in cfg.out_xml_attributes:
            append_to_key(row=row, key=key, prefix='@')
    to_output = {'data': {'row': rows}}
    encoding = cfg.output_encoding()
    with open(file=filename, mode='w', encoding=encoding) as file:
        xmltodict.unparse(to_output, output=file, pretty=True,
                          encoding=encoding)


def handle_json_output(data: Data | JsonType, filename: str,
                       cfg: ExtractConfig) -> None:
    """Handle output to JSON file."""
    json_output(data=data, filename=filename, encoding=cfg.output_encoding())
