#! /usr/local/bin/python3
"""Parameter data for extract-list configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional, TypedDict
from extract_list.config_enums import FormatRequest, InFileType, \
    MissingInputForColumn


class CsvSpec(TypedDict, total=False):
    """CSV dialect specification."""

    name: str
    delimiter: Optional[str]
    quoting: Optional[str]
    quotechar: Optional[str]
    lineterminator: Optional[str]
    escapechar: Optional[str]


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

    def __init__(self) -> None:
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
        self.outfile_type: str = 'excel'
        self.outfile_encoding: str = 'utf-8'
        self.outfile_implementation: Optional[str] = None
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number', 'key col']
        self.order_rows_by: list[str] = []
        self.out_xml_attributes = ['What']
        self.out_csv_dialect: CsvSpec = {'name': 'csv.excel',
                                         'delimiter': ',',
                                         'quoting': None,
                                         'quotechar': '"',
                                         'lineterminator': None,
                                         'escapechar': None}
