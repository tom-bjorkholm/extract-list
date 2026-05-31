#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, TextIO, cast
from enum import Enum
import sys
from copy import deepcopy
from config_as_json import CharEncodingValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, \
    MemberValidationStep, NestedConfigs, ParseConverter, PathOrStr, \
    ReadOldConfiguration, StrValidator, ValidationPlan, \
    WholeConfigValidationStep, ListIsOrderedValidator, \
    OptionalMemberValidator, ValueTypeValidator, ListValueTypeValidator, \
    string_to_enum_best_match, migrate_cfg
from tableio import FileAccess
from tableio_cfg_json import TioJsonConfig
from extract_list.config_enums import FormatRequest, InFileType, \
    INTERNAL_OUTFILE_FORMATS, MissingInputForColumn, \
    get_outfile_capabilities, is_internal_out_file_format
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineList, LinkedLineSpec, MainLineSpec, _mline_spec_from_dict, \
    _linked_line_from_json_array
from extract_list.validators import ExtractedColumnNameValidator, \
    OutputSelectionValidator, XmlColumnNameValidator


_MISSING = object()
_OLD_OUTPUT_KEYS = [
    'outfile_type', 'outfile_encoding', 'outfile_implementation',
    'out_csv_dialect', 'outfile_excel_library']


def _internal_format_name(format_name: str) -> str:
    """Return the normal spelling of an internal output format."""
    for internal_format in INTERNAL_OUTFILE_FORMATS:
        if internal_format.lower() == format_name.lower():
            return internal_format
    return format_name


def _old_csv_dialect_name(value: object) -> object:
    """Convert an old CSV dialect name to a TableIO dialect name."""
    if not isinstance(value, str):
        return value
    if value.lower() in ('csv.excel', 'csv.excel_tab'):
        return 'EXCEL'
    if value.lower() == 'csv.unix_dialect':
        return 'UNIX'
    return value


def _old_csv_quoting_name(value: object) -> object:
    """Convert an old CSV quoting name to a TableIO quoting name."""
    if not isinstance(value, str):
        return value
    quoting_map = {
        'csv.quote_all': 'all',
        'csv.quote_minimal': 'minimal',
        'csv.quote_none': 'none',
        'csv.quote_nonnumeric': 'nonnumeric'
    }
    return quoting_map.get(value.lower(), value)


def _old_csv_config(value: object) -> object:
    """Convert old out_csv_dialect data to a tableio-cfg-json csv section."""
    if not isinstance(value, dict):
        return value
    csv_config: dict[str, object] = {}
    old_name = value.get('name')
    for key, item_value in value.items():
        assert isinstance(key, str)
        if key == 'name':
            csv_config['dialect'] = _old_csv_dialect_name(item_value)
        elif key == 'quoting':
            csv_config['quoting'] = _old_csv_quoting_name(item_value)
        else:
            csv_config[key] = item_value
    if isinstance(old_name, str) and old_name.lower() == 'csv.excel_tab':
        if csv_config.get('delimiter') is None:
            csv_config['delimiter'] = '\t'
    return csv_config


def _pop_old_key(json_data: dict[str, object],
                 auto_ch_hook: ConfigAutoChangeHook, old_key: str) -> object:
    """Remove one old key and report that it was handled."""
    if old_key not in json_data:
        return _MISSING
    auto_ch_hook.old_key_handled(old_key)
    return json_data.pop(old_key)


def _remove_old_output_keys(json_data: dict[str, object],
                            auto_ch_hook: ConfigAutoChangeHook) -> None:
    """Remove old output keys when current output configuration wins."""
    for old_key in _OLD_OUTPUT_KEYS:
        _pop_old_key(json_data=json_data, auto_ch_hook=auto_ch_hook,
                     old_key=old_key)


class ExtractConfigOldReader(ReadOldConfiguration):
    """Normalize old extract-list output configuration keys."""

    def pre_process_json(self, json_data: dict[str, object],
                         auto_ch_hook: ConfigAutoChangeHook,
                         stderr_file: TextIO) -> dict[str, object]:
        """Move old output keys into the current output shape."""
        _ = stderr_file
        if 'output' in json_data or 'internal_output_format' in json_data:
            _remove_old_output_keys(json_data=json_data,
                                    auto_ch_hook=auto_ch_hook)
            return json_data
        old_format = _pop_old_key(json_data=json_data,
                                  auto_ch_hook=auto_ch_hook,
                                  old_key='outfile_type')
        if old_format is _MISSING:
            _remove_old_output_keys(json_data=json_data,
                                    auto_ch_hook=auto_ch_hook)
            return json_data
        old_encoding = _pop_old_key(json_data=json_data,
                                    auto_ch_hook=auto_ch_hook,
                                    old_key='outfile_encoding')
        old_implementation = _pop_old_key(json_data=json_data,
                                          auto_ch_hook=auto_ch_hook,
                                          old_key='outfile_implementation')
        old_csv = _pop_old_key(json_data=json_data, auto_ch_hook=auto_ch_hook,
                               old_key='out_csv_dialect')
        _pop_old_key(json_data=json_data, auto_ch_hook=auto_ch_hook,
                     old_key='outfile_excel_library')
        if isinstance(old_format, str) and \
                is_internal_out_file_format(old_format):
            json_data['output'] = None
            json_data['internal_output_format'] = \
                _internal_format_name(old_format)
            if old_encoding is _MISSING:
                json_data['internal_output_encoding'] = 'utf-8'
            else:
                json_data['internal_output_encoding'] = old_encoding
            return json_data
        output: dict[str, object] = {'format_name': old_format}
        if old_encoding is not _MISSING:
            output['character_encoding'] = old_encoding
        if old_implementation is not _MISSING and \
                old_implementation is not None:
            output['implementation'] = old_implementation
        if old_csv is not _MISSING:
            output['csv'] = _old_csv_config(old_csv)
        json_data['output'] = output
        return json_data

    def post_process_json(self, json_data: dict[str, object],
                          auto_ch_hook: ConfigAutoChangeHook,
                          stderr_file: TextIO) -> dict[str, object]:
        """Fill omitted optional output sentinels before validation."""
        _ = auto_ch_hook, stderr_file
        if 'outfile_border' not in json_data:
            json_data['outfile_border'] = FormatRequest.NO
        if 'outfile_filtered_area' not in json_data:
            json_data['outfile_filtered_area'] = FormatRequest.IF_AVAILABLE
        if 'output' not in json_data:
            json_data['output'] = None
        if 'internal_output_format' in json_data and \
                'internal_output_encoding' not in json_data:
            json_data['internal_output_encoding'] = 'utf-8'
        return json_data


class ExtractConfig(ExtractConfigParams, Config):
    """Configuration of extract a list of columns from JSON or XML."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Construct extract configuration object."""
        ExtractConfigParams.__init__(self, stderr_file=stderr_file)
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file)
        self._check_self()

    def _output_factory(self, from_json_data_text: Optional[str] = None,
                        from_json_filename: Optional[PathOrStr] = None,
                        stderr_file: TextIO = sys.stderr) -> TioJsonConfig:
        """Create nested TableIO output configuration from JSON."""
        capabilities = get_outfile_capabilities(
            border=self.outfile_border,
            filtered_area=self.outfile_filtered_area)
        return TioJsonConfig(capabilities=capabilities,
                             file_access=FileAccess.CREATE,
                             from_json_data_text=from_json_data_text,
                             from_json_filename=from_json_filename,
                             stderr_file=stderr_file)

    def nested_configs(self) -> NestedConfigs:
        """Get nested configuration declarations."""
        return {
            'output': ConfigNesting(kind=ConfigNestingKind.OPTIONAL_MEMBER,
                                    config_type=TioJsonConfig,
                                    factory_function=self._output_factory)
        }

    def _get_read_old_configuration(self) -> ReadOldConfiguration:
        """Return old-file compatibility rules."""
        return ExtractConfigOldReader()

    def _check_self(self) -> None:
        """Check that configuration is OK after reading from file or str."""
        self._check_mainline_part(var=self.main_line, spectype=MainLineSpec,
                                  varname='main_line')
        self._check_linkedline(self.linked_lines, 'linked_lines')
        self.cross_check_columns()
        self.cross_check_attrs()

    def _extracted_columns(self) -> list[str]:
        """Get list names of all extracted columns."""
        extracted_cols: list[str] = []
        for link in self.linked_lines:
            extracted_cols += link.columns.keys()
        extracted_cols += self.main_line.columns.keys()
        if self.include_key:
            extracted_cols.append(self.column_name_for_key)
        return extracted_cols

    def get_order_rows_by(self) -> list[str]:
        """Get list of columns to use for sorting rows."""
        if self.order_rows_by:
            return self.order_rows_by
        return self.column_order

    def cross_check_attrs(self) -> None:
        """Check that out_xml_attributes refer to existing 'columns'."""
        extracted_cols = self._extracted_columns()
        for att in self.out_xml_attributes:
            if att not in extracted_cols:
                print(f'Attribute name "{att}" in out_xml_attributes\n' +
                      'but no column with that name extracted',
                      file=sys.stderr)
                sys.exit(1)

    def cross_check_columns(self) -> None:
        """Do cross-check column order to extracted columns."""
        extracted_cols = self._extracted_columns()
        for col in self.column_order:
            if col not in extracted_cols:
                print(f'column order includes column "{col}"\n' +
                      'but that column is not extracted', file=sys.stderr)
                sys.exit(1)
        for col in extracted_cols:
            if col not in self.column_order:
                print(f'Extracted column "{col}" is missing in column_order',
                      file=sys.stderr)
                sys.exit(1)
        for col in self.order_rows_by:
            if col not in extracted_cols:
                print(f'order rows by includes column "{col}"\n' +
                      'but that column is not extracted', file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def _check_mainline_part(var: MainLineSpec | LinkedLineSpec,
                             spectype:
                             type[MainLineSpec] | type[LinkedLineSpec],
                             varname: str) -> None:
        """Check MainLineSpec or MainLineSpec part of LinkedLineSpec."""
        if not isinstance(var, spectype):
            print(f'Expected {spectype.__name__} for {varname}, but found: \n'
                  f'{var}\nof type {type(var).__name__}',
                  file=sys.stderr)
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
                      f'of type {type(elem).__name__}',
                      file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def get_converter_dict(enum_type: type[Enum]) -> ParseConverter:
        """Get dict for converting to given enum_type."""
        return ParseConverter(result_type=enum_type,
                              func=string_to_enum_best_match,
                              args={'num_type': enum_type})

    @staticmethod
    def get_converter_mainline(nttype: type[MainLineSpec]) -> ParseConverter:
        """Get dict for converting to given namedtuple type."""
        return ParseConverter(result_type=nttype, func=_mline_spec_from_dict,
                              args={})

    @staticmethod
    def get_converter_linkedline() -> ParseConverter:
        """Get dict for converting to linked_lines."""
        return ParseConverter(result_type=LinkedLineList,
                              func=_linked_line_from_json_array, args={})

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
                'outfile_border': self.get_converter_dict(FormatRequest),
                'outfile_filtered_area':
                    self.get_converter_dict(FormatRequest),
                'missing_input_for_column':
                    self.get_converter_dict(MissingInputForColumn),
                'main_line': self.get_converter_mainline(MainLineSpec),
                'linked_lines': self.get_converter_linkedline()}

    def _omit_none_from_json(self) -> list[str]:
        """Get list of keys that shall be omitted from JSON if None."""
        return ['output', 'internal_output_format',
                'internal_output_encoding']

    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Get validation plan for the configuration."""
        _ = stderr_file
        internal_format_val = OptionalMemberValidator(
            validator=StrValidator(allowed_values=INTERNAL_OUTFILE_FORMATS,
                                   ignore_case=True, best_match=True,
                                   normalize=True))
        opt_encoding_val = OptionalMemberValidator(
            validator=CharEncodingValidator())
        opt_output_val = OptionalMemberValidator(
            validator=ValueTypeValidator(TioJsonConfig))
        unique_val = ListIsOrderedValidator(element_type=str, is_ordered=False,
                                            unique_values=True)
        list_str_val = ListValueTypeValidator(str)
        return [
            MemberValidationStep(['infile_type'],
                                 ValueTypeValidator(InFileType)),
            MemberValidationStep(['outfile_border',
                                  'outfile_filtered_area'],
                                 ValueTypeValidator(FormatRequest)),
            MemberValidationStep(['missing_input_for_column'],
                                 ValueTypeValidator(MissingInputForColumn)),
            MemberValidationStep(['in_xml_strip_at', 'include_key',
                                  'one_output_line_per_main_line'],
                                 ValueTypeValidator(bool)),
            MemberValidationStep(['column_name_for_key'],
                                 ValueTypeValidator(str)),
            MemberValidationStep(['output'], opt_output_val),
            MemberValidationStep(['internal_output_format'],
                                 internal_format_val),
            MemberValidationStep(['internal_output_encoding'],
                                 opt_encoding_val),
            MemberValidationStep(['column_order', 'order_rows_by',
                                  'out_xml_attributes'], list_str_val),
            MemberValidationStep(['column_order'], unique_val),
            MemberValidationStep(['infile_encoding'], CharEncodingValidator()),
            MemberValidationStep(['column_order'], XmlColumnNameValidator()),
            WholeConfigValidationStep(ExtractedColumnNameValidator()),
            WholeConfigValidationStep(OutputSelectionValidator())
        ]

    def as_json_string(self, stderr_file: TextIO = sys.stderr) -> str:
        """Get JSON string representing this object."""
        if isinstance(self.main_line, dict):
            return super().as_json_string(stderr_file=stderr_file)
        adjusted = deepcopy(self)
        # intentionally violating typing to get wanted JSON
        adjusted.main_line = cast(MainLineSpec, self.main_line.__dict__)
        adjusted.linked_lines = []
        for i in self.linked_lines:
            # intentionally violating typing to get wanted JSON
            adjusted.linked_lines.append(cast(LinkedLineSpec, i.__dict__))
        return adjusted.as_json_string(stderr_file=stderr_file)


def migrate_cfg_func(in_filename: str, out_filename: str,
                     stderr_file: TextIO) -> int:
    """Migrate configuration file to new format."""
    return migrate_cfg(infile=in_filename, outfile=out_filename,
                       config_class=ExtractConfig, stderr_file=stderr_file)
