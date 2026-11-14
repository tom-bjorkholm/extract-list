#! /usr/local/bin/python3
"""Parameter data for extract-list configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional, TextIO, TypedDict, override
import sys
from config_as_json import Config, DictKeyValueTypesValidator, \
    ListForEachValidator, ListValueTypeValidator, MemberValidationStep, \
    PathOrStr, ValidationPlan
from tableio import FileAccess
from extract_list.config_enums import FormatRequest, InFileType, \
    MissingInputForColumn, get_outfile_capabilities
from extract_list.output_config import ExtractOutputConfig


MLineDict = TypedDict('MLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'expand_at': list[list[str]]})
LLineDict = TypedDict('LLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'linked_main_column': list[str],
                                    'linked_column': list[str],
                                    'expand_at': list[list[str]]})


class LineSpecBase(Config):
    """Members that the specifications of main and linked lines share.

    The main line and the linked lines are siblings deriving from this, as
    a linked line specification cannot be used as a main line one.
    """

    def __init__(self, data: Optional[MLineDict] = None,
                 from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Construct the shared members from data, JSON or else empty."""
        # The column names are chosen by the user, so the keys of columns
        # are checked by the validation plan and not against the default.
        self._unchecked_dicts: list[str] = ['columns']
        self.line: list[str] = [] if data is None else data['line']
        self.columns: dict[str, list[str]] = \
            {} if data is None else data['columns']
        self.expand_at: list[list[str]] = \
            [] if data is None else data['expand_at']
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         stderr_file=stderr_file, member_name=member_name)

    def __str__(self) -> str:
        """Get the class name and the public members."""
        public = {name: value for name, value in vars(self).items()
                  if not name.startswith('_')}
        return f'{type(self).__name__}({public})'

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Return validation of the shared members."""
        _ = stderr_file
        list_str = ListValueTypeValidator(str)
        return [
            MemberValidationStep(['line'], list_str),
            MemberValidationStep(['columns'], DictKeyValueTypesValidator(
                key_type=str, value_type=list, value_validator=list_str)),
            MemberValidationStep(['expand_at'], ListForEachValidator(
                element_validators=[list_str]))]


class MainLineSpec(LineSpecBase):
    """Specification for one input main line."""


class LinkedLineSpec(LineSpecBase):
    """Specification for one input linked line."""

    def __init__(self, data: Optional[LLineDict] = None,
                 from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Construct linked line specification from data, JSON or empty."""
        # Config requires every member to be set before it is constructed.
        self.linked_main_column: list[str] = \
            [] if data is None else data['linked_main_column']
        self.linked_column: list[str] = \
            [] if data is None else data['linked_column']
        super().__init__(data=data, from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         stderr_file=stderr_file, member_name=member_name)

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Return validation of the shared and the linking members."""
        link_step = MemberValidationStep(
            ['linked_main_column', 'linked_column'],
            ListValueTypeValidator(str))
        return super().get_validation_plan(stderr_file) + [link_step]


class ExtractConfigParams:  # pylint: disable=too-many-instance-attributes
    """Parameters for extracting a list of columns from JSON or XML."""

    @staticmethod
    def default_output_config(
            stderr_file: TextIO = sys.stderr) -> ExtractOutputConfig:
        """Get default configuration for output."""
        capabilities = get_outfile_capabilities()
        config = ExtractOutputConfig(capabilities=capabilities,
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
        self.output: ExtractOutputConfig = self.default_output_config(
            stderr_file=stderr_file)
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number', 'key col']
        self.order_rows_by: list[str] = []
        self.out_xml_attributes: list[str] = ['What']

    def output_encoding(self) -> str:
        """Get the configured output character encoding."""
        if self.output.character_encoding is None:
            return 'utf-8'
        return self.output.character_encoding
