#! /usr/local/bin/python3
"""Parameter data for extract-list configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional, TextIO, TypedDict
import sys
from tableio import FileAccess
from tableio_cfg_json import TioJsonConfig, tio_json_config_default
from extract_list.config_enums import FormatRequest, InFileType, \
    MissingInputForColumn, get_outfile_capabilities, \
    is_internal_out_file_format


MLineDict = TypedDict('MLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'expand_at': list[list[str]]})
LLineDict = TypedDict('LLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'linked_main_column': list[str],
                                    'linked_column': list[str],
                                    'expand_at': list[list[str]]})


class MainLineSpec:  # pylint: disable=too-few-public-methods
    """Specification for one input main line."""

    def __init__(self, data: Optional[MLineDict] = None) -> None:
        """Construct main line specification."""
        self.line: list[str] = []
        self.columns: dict[str, list[str]] = {}
        self.expand_at: list[list[str]] = []
        if data is not None:
            self.line = data['line']
            self.columns = data['columns']
            self.expand_at = data['expand_at']

    def __str__(self) -> str:
        """Get string representation."""
        return 'MainLineSpec(' + str(self.__dict__) + ')'


class LinkedLineSpec:  # pylint: disable=too-few-public-methods
    """Specification for one input linked line."""

    def __init__(self, data: Optional[LLineDict] = None) -> None:
        """Construct linked line specification."""
        self.line: list[str] = []
        self.columns: dict[str, list[str]] = {}
        self.linked_main_column: list[str] = []
        self.linked_column: list[str] = []
        self.expand_at: list[list[str]] = []
        if data is not None:
            self.line = data['line']
            self.columns = data['columns']
            self.linked_main_column = data['linked_main_column']
            self.linked_column = data['linked_column']
            self.expand_at = data['expand_at']

    def __str__(self) -> str:
        """Get string representation."""
        return 'LinkedLineSpec(' + str(self.__dict__) + ')'


class LinkedLineList(list[LinkedLineSpec]):
    """Type trick for JSON parser."""


def _mline_spec_from_dict(data: MLineDict) -> MainLineSpec:
    """Get main line specification converted from dict."""
    return MainLineSpec(data=data)


def _linked_line_from_json_array(data: list[LLineDict]) -> LinkedLineList:
    """Get list of LinkedLineSpec from list of dict."""
    assert isinstance(data, list)
    ret = []
    for elem in data:
        ret.append(LinkedLineSpec(data=elem))
    return LinkedLineList(ret)


class ExtractConfigParams:  # pylint: disable=too-many-instance-attributes
    """Parameters for extracting a list of columns from JSON or XML."""

    @staticmethod
    def default_output_config(
            stderr_file: TextIO = sys.stderr) -> TioJsonConfig:
        """Get default configuration for TableIO output."""
        capabilities = get_outfile_capabilities()
        config = tio_json_config_default(capabilities=capabilities,
                                         file_access=FileAccess.CREATE,
                                         stderr_file=stderr_file)
        config.character_encoding = 'utf-8'
        return config

    @staticmethod
    def example_main_line() -> MainLineSpec:
        """Get example spec for main line."""
        main_col = {'What': ['items', 'item'],
                    'How many': ['items', 'quantity']}
        data: MLineDict = {'line': ['orders'], 'columns': main_col,
                           'expand_at': [['items']]}
        return MainLineSpec(data=data)

    @staticmethod
    def example_linked_line() -> LinkedLineSpec:
        """Get example spec for linked line."""
        columns = {'Customer name': ['name'],
                   'Street': ['address', 'street'],
                   'Street number': ['address', 'number']}
        data: LLineDict = {'line': ['customers'], 'columns': columns,
                           'linked_main_column': ['customer'],
                           'linked_column': ['customer_number'],
                           'expand_at': []}
        return LinkedLineSpec(data=data)

    def __init__(self, stderr_file: TextIO = sys.stderr) -> None:
        """Initialize all configuration parameters to default values."""
        self.infile_type: InFileType = InFileType.JSON
        self.infile_encoding: str = 'utf-8'
        self.in_xml_strip_at: bool = False
        self.include_key: bool = True
        self.column_name_for_key: str = 'key col'
        self.missing_input_for_column: MissingInputForColumn = \
            MissingInputForColumn.EMPTY
        self.main_line: MainLineSpec = self.example_main_line()
        self.linked_lines: list[LinkedLineSpec] = [self.example_linked_line()]
        self.one_output_line_per_main_line: bool = True
        self.outfile_border: FormatRequest = FormatRequest.NO
        self.outfile_filtered_area: FormatRequest = FormatRequest.NO
        self.output: Optional[TioJsonConfig] = self.default_output_config(
            stderr_file=stderr_file)
        self.internal_output_format: Optional[str] = None
        self.internal_output_encoding: Optional[str] = None
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number', 'key col']
        self.order_rows_by: list[str] = []
        self.out_xml_attributes = ['What']

    def set_output_format(self, output_format: str,
                          stderr_file: TextIO = sys.stderr) -> None:
        """Set either a TableIO or internal output format."""
        if is_internal_out_file_format(output_format):
            self.output = None
            self.internal_output_format = output_format
            if self.internal_output_encoding is None:
                self.internal_output_encoding = 'utf-8'
            return
        if self.output is None:
            self.output = self.default_output_config(stderr_file=stderr_file)
        self.output.format_name = output_format
        self.internal_output_format = None
        self.internal_output_encoding = None

    def output_format_name(self) -> str:
        """Get the configured output format name."""
        if self.internal_output_format is not None:
            return self.internal_output_format
        if self.output is None:
            raise ValueError('No output format is configured.')
        if self.output.format_name is None:
            raise ValueError('No TableIO output format is configured.')
        return self.output.format_name

    def output_encoding(self) -> str:
        """Get the configured output character encoding."""
        if self.internal_output_format is not None:
            if self.internal_output_encoding is None:
                return 'utf-8'
            return self.internal_output_encoding
        if self.output is None or self.output.character_encoding is None:
            return 'utf-8'
        return self.output.character_encoding
