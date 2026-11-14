#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, TextIO
from enum import Enum
import sys
from config_as_json import CharEncodingValidator, Config, \
    ConfigAutoChangeHook, ConfigNesting, ConfigNestingKind, \
    ConfigPath, MemberValidationStep, NestedConfigs, ParseConverter, \
    PathOrStr, ReadOldConfiguration, RocfKeyMove, ValidationPlan, \
    WholeConfigValidationStep, ListIsOrderedValidator, \
    ValueTypeValidator, ListValueTypeValidator, \
    string_to_enum_best_match, migrate_cfg
from tableio import FileAccess
from extract_list.config_enums import FormatRequest, InFileType, \
    MissingInputForColumn, get_outfile_capabilities, list_out_file_formats
from extract_list.extract_config_params import ExtractConfigParams, \
    LinkedLineSpec, MainLineSpec
from extract_list.output_config import ExtractOutputConfig
from extract_list.validators import ColumnReferenceValidator, \
    ExtractedColumnNameValidator, XmlColumnNameValidator


def _old_0214_format_name(value: object) -> object:
    """Return the current output format for one 0.2.14 output type."""
    if not isinstance(value, str):
        return value
    format_names = {
        'excel': 'Excel',
        'csv': 'CSV',
        'json': 'JSON',
        'xml': 'XML',
        'txt': 'Plaintxt'
    }
    return format_names.get(value.lower(), value)


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


class ExtractConfigOldReader(ReadOldConfiguration):
    """Normalize released 0.2.14 output configuration keys."""

    def get_missing_path_values(self) -> dict[ConfigPath, object]:
        """Return current values for paths missing from old files."""
        return {('outfile_border',): FormatRequest.NO,
                ('outfile_filtered_area',): FormatRequest.IF_AVAILABLE}

    def get_json_key_moves(self) -> list[RocfKeyMove]:
        """Return old paths that should be moved to current output paths."""
        return [
            RocfKeyMove(old_path=('outfile_type',),
                        new_path=('output', 'format_name'),
                        transform_value=_old_0214_format_name),
            RocfKeyMove(old_path=('outfile_encoding',),
                        new_path=('output', 'character_encoding')),
            RocfKeyMove(old_path=('out_csv_dialect',),
                        new_path=('output', 'csv'),
                        transform_value=_old_csv_config)
        ]

    def get_keys_to_remove(self) -> list[ConfigPath]:
        """Return old output paths that no longer exist."""
        return [('outfile_excel_library',)]


class ExtractConfig(ExtractConfigParams, Config):
    """Configuration of extract a list of columns from JSON or XML."""

    def __init__(self, from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 auto_ch_hook: Optional[ConfigAutoChangeHook] = None,
                 stderr_file: TextIO = sys.stderr, *,
                 member_name: Optional[str] = None) -> None:
        """Construct extract configuration object."""
        ExtractConfigParams.__init__(self, stderr_file=stderr_file)
        Config.__init__(self, from_json_data_text=from_json_data_text,
                        from_json_filename=from_json_filename,
                        auto_ch_hook=auto_ch_hook, stderr_file=stderr_file,
                        member_name=member_name)

    def _output_factory(self, from_json_data_text: Optional[str] = None,
                        from_json_filename: Optional[PathOrStr] = None,
                        stderr_file: TextIO = sys.stderr, *,
                        member_name: Optional[str] = None) \
            -> ExtractOutputConfig:
        """Create nested output configuration from JSON."""
        capabilities = get_outfile_capabilities(
            border=self.outfile_border,
            filtered_area=self.outfile_filtered_area)
        return ExtractOutputConfig(
            capabilities=capabilities, file_access=FileAccess.CREATE,
            allowed_formats=list_out_file_formats(
                border=self.outfile_border,
                filtered_area=self.outfile_filtered_area),
            from_json_data_text=from_json_data_text,
            from_json_filename=from_json_filename, stderr_file=stderr_file,
            member_name=member_name)

    def nested_configs(self) -> NestedConfigs:
        """Get nested configuration declarations."""
        return {
            'output': ConfigNesting(kind=ConfigNestingKind.MEMBER,
                                    config_type=ExtractOutputConfig,
                                    factory_function=self._output_factory),
            'main_line': ConfigNesting(kind=ConfigNestingKind.MEMBER,
                                       config_type=MainLineSpec),
            'linked_lines': ConfigNesting(kind=ConfigNestingKind.LIST_ELEMENT,
                                          config_type=LinkedLineSpec)
        }

    def _get_read_old_config(self) -> ReadOldConfiguration:
        """Return old-file compatibility rules."""
        return ExtractConfigOldReader()

    def get_order_rows_by(self) -> list[str]:
        """Get list of columns to use for sorting rows."""
        if self.order_rows_by:
            return self.order_rows_by
        return self.column_order

    @staticmethod
    def get_converter_dict(enum_type: type[Enum]) -> ParseConverter:
        """Get dict for converting to given enum_type."""
        return ParseConverter(result_type=enum_type,
                              func=string_to_enum_best_match,
                              args={'num_type': enum_type})

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
                    self.get_converter_dict(MissingInputForColumn)}

    def _omit_none_from_json(self) -> list[str]:
        """Get list of keys that shall be omitted from JSON if None."""
        return []

    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Get validation plan for the configuration."""
        _ = stderr_file
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
            MemberValidationStep(['output'],
                                 ValueTypeValidator(ExtractOutputConfig)),
            MemberValidationStep(['column_order', 'order_rows_by',
                                  'out_xml_attributes'], list_str_val),
            MemberValidationStep(['column_order'], unique_val),
            MemberValidationStep(['infile_encoding'], CharEncodingValidator()),
            MemberValidationStep(['column_order'], XmlColumnNameValidator()),
            WholeConfigValidationStep(ExtractedColumnNameValidator()),
            WholeConfigValidationStep(ColumnReferenceValidator())
        ]


def migrate_cfg_func(in_filename: str, out_filename: str,
                     stderr_file: TextIO) -> int:
    """Migrate configuration file to new format."""
    return migrate_cfg(infile=in_filename, outfile=out_filename,
                       config_class=ExtractConfig, stderr_file=stderr_file)
