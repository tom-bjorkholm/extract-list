#! /usr/local/bin/python3
"""Define validators for extract list."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from string import whitespace
from typing import NoReturn, TextIO, cast
import sys
from config_as_json import Config, InvalidConfiguration, \
    MemberValidator, WholeConfigValidator
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineSpec, MainLineSpec


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


def _extracted_columns(config: ExtractConfigParams,
                       stderr_file: TextIO) -> list[str]:
    """Return names of all extracted columns."""
    extracted_columns: list[str] = []
    for linked_line in config.linked_lines:
        extracted_columns.extend(_column_names_from_spec(linked_line,
                                                         stderr_file))
    extracted_columns.extend(_column_names_from_spec(config.main_line,
                                                     stderr_file))
    if config.include_key:
        extracted_columns.append(config.column_name_for_key)
    return extracted_columns


def _repeated_names(names: list[str]) -> list[str]:
    """Return duplicate names in first repeated occurrence order."""
    seen_names: set[str] = set()
    repeated_name_set: set[str] = set()
    repeated_names: list[str] = []
    for name in names:
        if name in seen_names and name not in repeated_name_set:
            repeated_names.append(name)
            repeated_name_set.add(name)
        seen_names.add(name)
    return repeated_names


# pylint: disable-next=too-few-public-methods
class ExtractedColumnNameValidator(WholeConfigValidator):
    """Validate that extracted column names are unique."""

    def validate(self, config: Config,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Validate extracted column names in an extract-list config."""
        extract_config = _extract_config_params(config, stderr_file)
        column_names = _extracted_columns(extract_config, stderr_file)
        repeated_names = _repeated_names(column_names)
        if not repeated_names:
            return
        msg = 'Invalid configuration: Extracted column names must be unique.'
        msg += ' Repeated column name(s): '
        msg += ', '.join(repeated_names)
        _raise_invalid_configuration(msg, stderr_file)


# pylint: disable-next=too-few-public-methods
class XmlColumnNameValidator(MemberValidator):
    """Validate XML output column names."""

    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> object:
        """Validate XML column names in one config member."""
        extract_config = _extract_config_params(config, stderr_file)
        if extract_config.outfile_type.lower() != 'xml':
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
