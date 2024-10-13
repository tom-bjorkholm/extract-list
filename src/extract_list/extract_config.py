#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import Optional, NamedTuple, TypeAlias, TypeVar, cast
from enum import Enum
from csv import Dialect
import sys
from copy import deepcopy
from excel_list_transform.config import Config, ParseConverter
from excel_list_transform.config_enums import ExcelLib
from excel_list_transform.str_to_enum import string_to_enum_best_match
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


class LinkedLineList(list[LinkedLineSpec]):
    """Type trick for JSON parser."""


LineDict: TypeAlias = dict[str, list[str] | dict[str, list[str]]]
SomeNamedTuple = TypeVar('SomeNamedTuple', MainLineSpec, LinkedLineSpec)
SomeCfgTyp = TypeVar('SomeCfgTyp')


def _named_tuple_from_dict(data: LineDict,
                           named_tuple_type: type[SomeNamedTuple]) \
                               -> SomeNamedTuple:
    """Get named tuple converted from dict."""
    return named_tuple_type(**data)


def _linked_line_from_json_array(data: list[LineDict]) -> LinkedLineList:
    """Get list of LinkedLineSpec from list of dict."""
    assert isinstance(data, list)
    ret = []
    for elem in data:
        ret.append(_named_tuple_from_dict(elem, LinkedLineSpec))
    return LinkedLineList(ret)


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
        self._check_self()

    def get_out_csv_dialect(self) -> type[Dialect]:
        """Get CSV dialect for outpyt file."""
        assert self.out_csv_dialect['name'] is not None
        return self.get_csv_dialect(**self.out_csv_dialect)

    def _check_self(self) -> None:
        """Check that configuration is OK after reading from file."""
        self._check_filetype(self.infile_type, InFileType)
        self.check_char_encoding(self.infile_encoding)
        self._check_filetype(self.outfile_type, OutFileType)
        self.check_char_encoding(self.outfile_encoding)
        self._check_type(self.in_xml_strip_at, bool, 'in_xml_strip_at')
        self._check_type(self.include_key, bool, 'include_key')
        self._check_type(self.column_name_for_key, str, 'column_name_for_key')
        self._check_enum(self.missing_input_for_column, MissingInputForColumn,
                         'missing_input_for_column')
        self._check_type(self.main_line, MainLineSpec, 'main_line')
        self._check_mainline_part(var=self.main_line, spectype=MainLineSpec,
                                  varname='main_line')
        self._check_type(self.linked_lines, list, 'linked_lines')
        self._check_linkedline(self.linked_lines, 'linked_lines')
        self._check_enum(self.outfile_excel_library, ExcelLib,
                         'outfile_excel_library')
        self._check_type(self.column_order, list, 'column_order')
        self._check_list_str(self.column_order, 'column_order')
        self._check_type(self.out_xml_attributes, list, 'out_xml_attributes')
        self._check_list_str(self.out_xml_attributes, 'out_xml_attributes')
        # TODO check out_csv_dialect
        # TODO do cross-checking column order to extracted columns

    @staticmethod
    def _check_mainline_part(var: MainLineSpec | LinkedLineSpec,
                             spectype:
                             type[MainLineSpec] | type[LinkedLineSpec],
                             varname: str) -> None:
        """Check MainLineSpec or MainLineSpec part of LinkedLineSpec."""
        if not isinstance(var, spectype):
            print(f'Excpected {spectype.__name__} for {varname}, but found: \n'
                  f'{var}\nof type {type(var).__name__}')
            sys.exit(1)
        ExtractConfig._check_list_str(var.line, 'line in ' + varname)
        ExtractConfig._check_dict_str_lst_str(var.columns,
                                              'columns in ' + varname)

    @staticmethod
    def _check_linkedline(var: LinkedLineList | list[LinkedLineSpec],
                          varname: str) -> None:
        """Check that we have correct LinkedLineSpec list."""
        if not isinstance(var, list):
            print(f'Expected a list of LinkedLineSpec in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for elem in var:
            vname = 'element in ' + varname
            ExtractConfig._check_mainline_part(var=elem,
                                               spectype=LinkedLineSpec,
                                               varname=vname)
            ExtractConfig._check_list_str(elem.linked_main_column,
                                          'linked_main_column in ' + vname)
            ExtractConfig._check_list_str(elem.linked_column,
                                          'linked_column in ' + vname)

    @staticmethod
    def _check_dict_str_lst_str(var: dict[str, list[str]],
                                varname: str) -> None:
        """Check that var is dict[str, list[str]]."""
        if not isinstance(var, dict):
            print(f'Expected a dict of strings to lists in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for key, value in var.items():
            if not isinstance(key, str):
                print(f'Expected a dict of strings to lists in {varname}\n' +
                      f'but found key: {key}\nof type {type(key).__name__}',
                      file=sys.stderr)
                sys.exit(1)
            ExtractConfig._check_list_str(value, key + ' in ' + varname)

    @staticmethod
    def _check_list_str(var: list[str], varname: str) -> None:
        """Check that variable is list of str."""
        if not isinstance(var, list):
            print(f'Expected a list of strings in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for elem in var:
            if not isinstance(elem, str):
                print(f'Expected a list of strings in {varname}\n' +
                      f'but found element: {elem}\n' +
                      'of type {type(elem).__name__}',
                      file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def _check_enum(var: Enum, enum_type: type[Enum], varname: str) -> None:
        """Check that config variable is correct enum type."""
        ExtractConfig._check_type(var=var, oftype=enum_type, varname=varname)
        if var not in enum_type:
            allowed = ' ,'.join(list(enum_type))
            print(f'{varname} value {var} is not one of allowed: {allowed}',
                  file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _check_type(var: SomeCfgTyp, oftype: type[SomeCfgTyp],
                    varname: str) -> None:
        """Check that config variable is of type."""
        if not isinstance(var, oftype):
            print(f'Configuration parameter "{varname}" has wrong type.',
                  file=sys.stderr)
            print(f'Type is "{type(var).__name__}", ' +
                  f'but expected type "{oftype.__name__}".', file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _check_filetype(ftype: InFileType | OutFileType,
                        enum_type:
                        type[InFileType] | type[OutFileType]) -> None:
        """Check that file types are OK."""
        if not isinstance(ftype, enum_type):
            print(f'File type {ftype} is not of type {enum_type.__name__}',
                  file=sys.stderr)
            sys.exit(1)
        if ftype not in enum_type:
            allowed = ' ,'.join(list(enum_type))
            print(f'File type {ftype} is not one of allowed types: {allowed}',
                  file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def get_converter_dict(enum_type: type[Enum]) -> ParseConverter:
        """Get dict for converting to given enum_type."""
        return ParseConverter(result_type=enum_type,
                              func=string_to_enum_best_match,
                              args={'num_type': enum_type})

    @staticmethod
    def get_converter_namedtuple(nttype: type[NamedTuple]) -> ParseConverter:
        """Get dict for converting to given namedtuple type."""
        return ParseConverter(result_type=nttype,
                              func=_named_tuple_from_dict,
                              args={'named_tuple_type': nttype})

    @staticmethod
    def get_converter_linkedline() -> ParseConverter:
        """Get dict for converting to linked_lines."""
        return ParseConverter(result_type=LinkedLineList,
                              func=_linked_line_from_json_array,
                              args={})

    def parse_converters(self) -> dict[str, ParseConverter]:
        """Get converters for use when parsing JSON.

        Overriding in derived class.
        Return None if no conversions.
        Return dict of dict for use in json decoder hook.
        Structure of return value shall be:
        {key: {'result type': res_type, 'func': function,
        'args': {arg_name: arg_value}}}.
        """
        return {'infile_type': self.get_converter_dict(InFileType),
                'outfile_type': self.get_converter_dict(OutFileType),
                'outfile_excel_library': self.get_converter_dict(ExcelLib),
                'missing_input_for_column':
                    self.get_converter_dict(MissingInputForColumn),
                'main_line': self.get_converter_namedtuple(MainLineSpec),
                'linked_lines': self.get_converter_linkedline()}

    def as_json_string(self) -> str:
        """Get JSON string representing this object."""
        if isinstance(self.main_line, dict):
            return super().as_json_string()
        adjusted = deepcopy(self)
        # intentionally violating typing to get wanted JSON
        adjusted.main_line = cast(MainLineSpec, self.main_line._asdict())
        adjusted.linked_lines = []
        for i in self.linked_lines:
            # intentionally violating typing to get wanted JSON
            adjusted.linked_lines.append(cast(LinkedLineSpec, i._asdict()))
        return adjusted.as_json_string()
