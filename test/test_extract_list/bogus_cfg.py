#! /usr/local/bin/python3
"""Write a configuration file that fails validation, for tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import json
from pathlib import Path
from extract_list.extract_config import ExtractConfig


def write_bogus_cfg(filename: Path) -> None:
    """Write a configuration whose column_order has the unextracted "Bogus".

    Config.write validates before writing, so the JSON is changed directly.
    """
    data: dict[str, object] = json.loads(ExtractConfig().as_json_string())
    column_order = data['column_order']
    assert isinstance(column_order, list)
    column_order.append('Bogus')
    filename.write_text(json.dumps(data), encoding='utf-8')
