#! /usr/local/bin/python3
"""Write configuration files that cannot be read, for tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import json
import sys
from pathlib import Path
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


def write_cfg_without(filename: Path, linked: bool, key: str) -> None:
    """Write a configuration with key left out of one line specification.

    The key is left out of the first linked line if linked, else out of the
    main line.
    """
    data = _default_data()
    spec = data['main_line']
    if linked:
        linked_lines = data['linked_lines']
        assert isinstance(linked_lines, list)
        spec = linked_lines[0]
    assert isinstance(spec, dict)
    del spec[key]
    filename.write_text(json.dumps(data), encoding='utf-8')
