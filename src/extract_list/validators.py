#! /usr/local/bin/python3
"""Define validators for extract list."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from string import whitespace
from typing import NoReturn, Optional, TextIO, cast
import sys
from config_as_json import Config, InvalidConfiguration, \
    MemberValidator, WholeConfigValidator, member_path
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineSpec, MainLineSpec
from extract_list.member_paths import element_path


def _raise_invalid_configuration(message: str,
                                 stderr_file: TextIO) -> NoReturn:
    """Raise InvalidConfiguration with the given message."""
    print(message, file=stderr_file)
    raise InvalidConfiguration(message)


def _extract_config_params(config: Config,
                           stderr_file: TextIO) -> ExtractConfigParams:
    """Return config as extract-list configuration parameters."""
    if isinstance(config, ExtractConfigParams):
        return config
    msg = 'Invalid configuration: Expected ExtractConfigParams compatible '
    msg += 'config.'
    _raise_invalid_configuration(msg, stderr_file)


def _column_names_from_dict(spec: dict[object, object],
                            stderr_file: TextIO) -> list[str]:
    """Return column names from a JSON-friendly line spec dict."""
    columns = spec.get('columns')
    if not isinstance(columns, dict):
        msg = 'Invalid configuration: Line specification must contain a '
        msg += 'columns dict.'
        _raise_invalid_configuration(msg, stderr_file)
    column_names: list[str] = []
    for column_name in columns.keys():
        if not isinstance(column_name, str):
            msg = 'Invalid configuration: Extracted column name '
            msg += f'{column_name!r} is not a string.'
            _raise_invalid_configuration(msg, stderr_file)
        column_names.append(column_name)
    return column_names


def _column_names_from_spec(spec: object, stderr_file: TextIO) -> list[str]:
    """Return column names from a line specification object or dict."""
    if isinstance(spec, (MainLineSpec, LinkedLineSpec)):
        return list(spec.columns.keys())
    if isinstance(spec, dict):
        spec_dict = cast(dict[object, object], spec)
        return _column_names_from_dict(spec_dict, stderr_file)
    msg = 'Invalid configuration: Line specification has unexpected type '
    msg += f'{type(spec).__name__}.'
    _raise_invalid_configuration(msg, stderr_file)


def _add_column_paths(paths: dict[str, list[str]], spec: object,
                      line_path: str, stderr_file: TextIO) -> None:
    """Record where each column of one line specification is declared."""
    columns_path = member_path(line_path, 'columns')
    for name in _column_names_from_spec(spec, stderr_file):
        paths.setdefault(name, []).append(element_path(columns_path, name))


def _column_paths(config: ExtractConfigParams, stderr_file: TextIO,
                  member_name: Optional[str]) -> dict[str, list[str]]:
    """Return where each extracted column name is declared."""
    paths: dict[str, list[str]] = {}
    linked_path = member_path(member_name, 'linked_lines')
    for index, linked_line in enumerate(config.linked_lines):
        line_path = element_path(linked_path, index)
        _add_column_paths(paths, linked_line, line_path, stderr_file)
    _add_column_paths(paths, config.main_line,
                      member_path(member_name, 'main_line'), stderr_file)
    if config.include_key:
        paths.setdefault(config.column_name_for_key, []).append(
            member_path(member_name, 'column_name_for_key'))
    return paths


def _repeated_report(paths: dict[str, list[str]]) -> str:
    """Return the reported paths of the column names declared twice."""
    return '; '.join(f'{name} at ' + ', '.join(at)
                     for name, at in paths.items() if len(at) > 1)


# pylint: disable-next=too-few-public-methods
class ExtractedColumnNameValidator(WholeConfigValidator):
    """Validate that extracted column names are unique."""

    def validate(self, config: Config, stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Validate extracted column names in an extract-list config."""
        extract_config = _extract_config_params(config, stderr_file)
        paths = _column_paths(extract_config, stderr_file, member_name)
        repeated = _repeated_report(paths)
        if not repeated:
            return
        msg = 'Invalid configuration: Extracted column names must be unique.'
        msg += ' Repeated column name(s): ' + repeated
        _raise_invalid_configuration(msg, stderr_file)


# pylint: disable-next=too-few-public-methods
class XmlColumnNameValidator(MemberValidator):
    """Validate XML output column names."""

    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Validate XML column names in one config member."""
        extract_config = _extract_config_params(config, stderr_file)
        if extract_config.output.format_name.lower() != 'xml':
            return member_value
        assert isinstance(member_value, list)
        column_order = cast(list[str], member_value)
        invalid_names = [
            name for name in column_order
            if any(char in whitespace for char in name)]
        if not invalid_names:
            return member_value
        msg = 'Invalid configuration: XML output column names in '
        msg += f'{member_name} must not contain whitespace. '
        msg += 'Invalid column name(s): '
        msg += ', '.join(invalid_names)
        _raise_invalid_configuration(msg, stderr_file)
