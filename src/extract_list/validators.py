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
    LineSpecBase
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


def _add_column_paths(paths: dict[str, list[str]], spec: LineSpecBase,
                      line_path: str) -> None:
    """Record where each column of one line specification is declared.

    The line specifications are nested configurations, validated before
    this, so their columns are known to be a dict with string keys.
    """
    columns_path = member_path(line_path, 'columns')
    for name in spec.columns:
        paths.setdefault(name, []).append(element_path(columns_path, name))


def _column_paths(config: ExtractConfigParams,
                  member_name: Optional[str]) -> dict[str, list[str]]:
    """Return where each extracted column name is declared."""
    paths: dict[str, list[str]] = {}
    linked_path = member_path(member_name, 'linked_lines')
    for index, linked_line in enumerate(config.linked_lines):
        line_path = element_path(linked_path, index)
        _add_column_paths(paths, linked_line, line_path)
    _add_column_paths(paths, config.main_line,
                      member_path(member_name, 'main_line'))
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
        paths = _column_paths(extract_config, member_name)
        repeated = _repeated_report(paths)
        if not repeated:
            return
        msg = 'Invalid configuration: Extracted column names must be unique.'
        msg += ' Repeated column name(s): ' + repeated
        _raise_invalid_configuration(msg, stderr_file)


def _unknown_references(config: ExtractConfigParams, extracted: list[str],
                        member_name: Optional[str]) -> list[str]:
    """Return one problem per listed column that is not extracted."""
    references = {'column_order': config.column_order,
                  'order_rows_by': config.order_rows_by,
                  'out_xml_attributes': config.out_xml_attributes}
    return [f'{member_path(member_name, member)} includes column "{name}", '
            'but that column is not extracted'
            for member, names in references.items() for name in names
            if name not in extracted]


def _unordered_columns(config: ExtractConfigParams, extracted: list[str],
                       member_name: Optional[str]) -> list[str]:
    """Return one problem per extracted column missing in column_order."""
    order_path = member_path(member_name, 'column_order')
    return [f'extracted column "{name}" is missing in {order_path}'
            for name in extracted if name not in config.column_order]


# pylint: disable-next=too-few-public-methods
class ColumnReferenceValidator(WholeConfigValidator):
    """Validate that column lists refer to exactly the extracted columns.

    column_order must hold every extracted column and nothing else, while
    order_rows_by and out_xml_attributes may only hold extracted columns.
    All problems are reported in one message, so that a user fixing the
    configuration sees everything that is wrong at once.
    """

    def validate(self, config: Config, stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Validate column references in an extract-list config."""
        extract_config = _extract_config_params(config, stderr_file)
        extracted = list(_column_paths(extract_config, member_name))
        problems = _unknown_references(extract_config, extracted, member_name)
        problems += _unordered_columns(extract_config, extracted, member_name)
        if not problems:
            return
        msg = 'Invalid configuration: ' + '; '.join(problems) + '.'
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
