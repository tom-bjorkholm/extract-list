#! /usr/local/bin/python3
"""Test reading configuration JSON data that lacks keys.

Every Config constructor and Config factory of extract-list accepts
ok_to_use_defaults and passes it on. With it true a missing key keeps its
default value, at every nesting level, and with it false (the default) a
missing key is refused.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from collections.abc import Callable
from pathlib import Path
import json
import sys
import pytest
from config_as_json import Config, ConfigMissingKey, JsonPath
from tableio import FileAccess
from extract_list.config_enums import get_outfile_capabilities
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineSpec, MainLineSpec
from extract_list.extract_func import extract_func
from extract_list.output_config import ExtractOutputConfig
from .bogus_cfg import cfg_text_without, write_cfg_without
from .check_capsys import check_capsys

MISSING = [(('include_key',), 'include_key'),
           (('main_line',), 'main_line'),
           (('main_line', 'line'), 'main_line.line'),
           (('linked_lines',), 'linked_lines'),
           (('linked_lines', 0, 'linked_column'),
            'linked_lines[0].linked_column'),
           (('output',), 'output'),
           (('output', 'format_name'), 'output.format_name')]
"""Paths of keys to leave out, at every nesting level, and how they are
named in diagnostics. The output member is built by a factory."""


def _json_at(config: Config, path: JsonPath) -> object:
    """Return the JSON value at path in the JSON data of config."""
    value: object = json.loads(config.as_json_string(stderr_file=sys.stderr))
    for key in path:
        assert isinstance(value, (dict, list))
        value = value[key] if isinstance(value, dict) \
            else value[int(key)]
    return value


@pytest.mark.parametrize('path', [path for path, _ in MISSING])
def test_cfg_kept_paths(capsys: pytest.CaptureFixture[str],
                        path: JsonPath) -> None:
    """Test that a missing key is kept with ok_to_use_defaults true."""
    cfg = ExtractConfig(from_json_data_text=cfg_text_without(path),
                        stderr_file=sys.stderr, ok_to_use_defaults=True)
    assert cfg.kept_value_paths() == [path]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('path, expected',
                         [(('include_key',), True),
                          (('main_line', 'line'), ['orders']),
                          (('linked_lines', 0, 'linked_column'), []),
                          (('output', 'format_name'), 'Excel')])
def test_cfg_kept_values(capsys: pytest.CaptureFixture[str], path: JsonPath,
                         expected: object) -> None:
    """Test the values that missing keys keep.

    A nested member keeps the value it had. A list element and an object
    built by a factory are new, so they get the defaults of their class,
    which are empty lists for a linked line.
    """
    cfg = ExtractConfig(from_json_data_text=cfg_text_without(path),
                        stderr_file=sys.stderr, ok_to_use_defaults=True)
    assert _json_at(cfg, path) == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('path, member', MISSING)
def test_cfg_strict(capsys: pytest.CaptureFixture[str], path: JsonPath,
                    member: str) -> None:
    """Test that a missing key is refused without ok_to_use_defaults."""
    with pytest.raises(ConfigMissingKey):
        ExtractConfig(from_json_data_text=cfg_text_without(path),
                      stderr_file=sys.stderr)
    check_capsys(capsys=capsys, in_err=f'No value for {member} in JSON data')


@pytest.mark.parametrize('path, member', MISSING)
def test_extract_strict(capsys: pytest.CaptureFixture[str], tmp_path: Path,
                        path: JsonPath, member: str) -> None:
    """Test that the extract command refuses a file that lacks a key."""
    cfg_file = tmp_path / 'lacking.cfg'
    write_cfg_without(cfg_file, path)
    ret = extract_func(in_file_name=str(tmp_path / 'in.json'),
                       cfg_file_name=str(cfg_file),
                       out_file_name=str(tmp_path / 'out.csv'))
    assert ret == 1
    check_capsys(capsys=capsys, in_err=f'No value for {member} in JSON data')


def _main_line(text: str, ok_to_use_defaults: bool) -> Config:
    """Construct a main line specification from JSON text."""
    return MainLineSpec(from_json_data_text=text, stderr_file=sys.stderr,
                        ok_to_use_defaults=ok_to_use_defaults)


def _linked_line(text: str, ok_to_use_defaults: bool) -> Config:
    """Construct a linked line specification from JSON text."""
    return LinkedLineSpec(from_json_data_text=text, stderr_file=sys.stderr,
                          ok_to_use_defaults=ok_to_use_defaults)


def _output(text: str, ok_to_use_defaults: bool) -> Config:
    """Construct an output configuration from JSON text."""
    return ExtractOutputConfig(capabilities=get_outfile_capabilities(),
                               file_access=FileAccess.CREATE,
                               from_json_data_text=text,
                               stderr_file=sys.stderr,
                               ok_to_use_defaults=ok_to_use_defaults)


def _text_without(config: Config, key: str) -> str:
    """Return the JSON text of config without the top level key."""
    data = json.loads(config.as_json_string(stderr_file=sys.stderr))
    assert isinstance(data, dict)
    del data[key]
    return json.dumps(data)


NESTED = [(_main_line, ExtractConfigParams.example_main_line(), 'line'),
          (_linked_line, ExtractConfigParams.example_linked_line(),
           'linked_column'),
          (_output, ExtractConfigParams.default_output_config(),
           'format_name')]
"""Nested configuration classes, an object of each and a key to leave out."""


@pytest.mark.parametrize('make, config, key', NESTED)
def test_nested_kept(capsys: pytest.CaptureFixture[str],
                     make: Callable[[str, bool], Config], config: Config,
                     key: str) -> None:
    """Test that each nested class passes ok_to_use_defaults on."""
    cfg = make(_text_without(config, key), True)
    assert cfg.kept_value_paths() == [(key,)]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('make, config, key', NESTED)
def test_nested_strict(capsys: pytest.CaptureFixture[str],
                       make: Callable[[str, bool], Config], config: Config,
                       key: str) -> None:
    """Test that each nested class refuses a missing key by default."""
    with pytest.raises(ConfigMissingKey):
        make(_text_without(config, key), False)
    check_capsys(capsys=capsys, in_err=f'No value for {key} in JSON data')
