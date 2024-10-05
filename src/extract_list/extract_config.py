#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import Optional, NamedTuple, TypeAlias
from csv import Dialect
from excel_list_transform.config import Config
from excel_list_transform.config_enums import ExcelLib
from extract_list.config_enums import InFileType, OutFileType, \
    MissingInputForColumn

CsvSpec: TypeAlias = dict[str, Optional[str]]


class MainLineSpec(NamedTuple):
    """Spec how to find main line."""

    line: list[str]
    columns: dict[str, list[str]]


class LinkedLineSpec(NamedTuple):
    """Spec how to find linked line."""

    line: list[str]
    columns: dict[str, list[str]]
    linked_main_column: list[str]
    linked_column: list[str]


class ExtractConfig(Config):  # pylint: disable=too-many-instance-attributes
    """Configuration of extract a list of columns from JSON or XML."""

    @staticmethod
    def example_main_line() -> MainLineSpec:
        """Get example spec for main line."""
        main_col = {'What': ['item'], 'How many': ['quantity']}
        return MainLineSpec(line=['orders'],
                            columns=main_col)

    @staticmethod
    def example_linked_line() -> LinkedLineSpec:
        """Get example spec for linked line."""
        columns = {'Customer name': ['name'],
                   'Street': ['address', 'street'],
                   'Street number': ['address', 'numer']}
        return LinkedLineSpec(line=['customers'],
                              columns=columns,
                              linked_main_column=['customer_number'],
                              linked_column=['customer'])

    def __init__(self,  from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[str] = None) -> None:
        """Construct extract configuration object."""
        self.infile_type: InFileType = InFileType.JSON
        self.infile_encoding: str = 'utf-8'
        self.in_xml_strip_at: bool = False
        self.in_xml_strip_hash: bool = False
        self.include_key: bool = True
        self.column_name_for_key: str = 'key col'
        self.missing_input_for_column: MissingInputForColumn = \
            MissingInputForColumn.EMPTY
        self.main_line: MainLineSpec = self.example_main_line()
        self.linked_lines: list[LinkedLineSpec] = [self.example_linked_line()]
        self.outfile_type: OutFileType = OutFileType.EXCEL
        self.outfile_encoding: str = 'utf-8'
        self.outfile_excel_library: ExcelLib = ExcelLib.PYLIGHTXL
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number']
        self.out_xml_attributes = ['What']
        self.out_csv_dialect: CsvSpec = {'name': 'csv.excel',
                                         'delimiter': ',', 'quoting': None,
                                         'quotechar': '"',
                                         'lineterminator': None,
                                         'escapechar': None}
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename)
        # do checking

    def get_out_csv_dialect(self) -> type[Dialect]:
        """Get CSV dialect for outpyt file."""
        assert self.out_csv_dialect['name'] is not None
        return self.get_csv_dialect(**self.out_csv_dialect)
