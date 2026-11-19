#! /usr/local/bin/python3
"""Write configuration files that cannot be read, for tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import json
import sys
from pathlib import Path
from config_as_json import JsonPath
from extract_list.extract_config import ExtractConfig


def _default_data() -> dict[str, object]:
    """Return the default configuration as JSON data.

    Config.write validates before writing, so the tests change this JSON
    data directly.
    """
    data = json.loads(ExtractConfig().as_json_string(stderr_file=sys.stderr))
    assert isinstance(data, dict)
    return data


def write_bogus_cfg(filename: Path) -> None:
    """Write a configuration whose column_order has the unextracted "Bogus"."""
    data = _default_data()
    column_order = data['column_order']
    assert isinstance(column_order, list)
    column_order.append('Bogus')
    filename.write_text(json.dumps(data), encoding='utf-8')


def _child(node: object, key: str | int) -> object:
    """Return the value at key in a JSON object or array."""
    if isinstance(node, list):
        assert isinstance(key, int)
        return node[key]
    assert isinstance(node, dict)
    return node[key]


def cfg_text_without(path: JsonPath) -> str:
    """Return the default configuration as JSON text, without path.

    The last key of path is a key of a JSON object.
    """
    data = _default_data()
    parent: object = data
    for key in path[:-1]:
        parent = _child(parent, key)
    assert isinstance(parent, dict)
    del parent[path[-1]]
    return json.dumps(data)


def write_cfg_without(filename: Path, path: JsonPath) -> None:
    """Write the default configuration with the value at path left out."""
    filename.write_text(cfg_text_without(path), encoding='utf-8')
