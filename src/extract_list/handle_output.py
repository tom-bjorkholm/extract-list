#! /usr/local/bin/python3
"""Produce output to file in chosen format."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

import sys
from pathlib import Path
from typing import Optional
from config_as_json.file_extension import fix_file_extension
from tableio import CsvDialect, FileAccess, OptionalArgsDict, \
    TableBorderStyle, create_tableio, filter_args_tableio
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import Data
from extract_list.config_enums import FormatRequest, \
    get_outfile_capabilities, is_internal_out_file_format
from extract_list.handle_json_xml_output import \
    handle_json_output, handle_xml_output


def _csv_dialect_name_to_tableio(name: Optional[str]) -> Optional[CsvDialect]:
    """Convert configured CSV dialect name to TableIO CSV dialect."""
    if name is None:
        return None
    if name.lower() in ('csv.excel', 'csv.excel_tab'):
        return CsvDialect.EXCEL
    if name.lower() == 'csv.unix_dialect':
        return CsvDialect.UNIX
    raise KeyError(f'Unknown csv dialect: {name}')


def _csv_quoting_to_tableio(quoting: Optional[str]) -> Optional[str]:
    """Convert configured CSV quoting name to TableIO CSV quoting."""
    if quoting is None:
        return None
    quoting_map = {
        'csv.quote_all': 'all',
        'csv.quote_minimal': 'minimal',
        'csv.quote_none': 'none',
        'csv.quote_nonnumeric': 'nonnumeric'
    }
    return quoting_map[quoting.lower()]


def _csv_delimiter_to_tableio(cfg: ExtractConfig) -> Optional[str]:
    """Get configured CSV delimiter for TableIO."""
    delimiter = cfg.out_csv_dialect['delimiter']
    name = cfg.out_csv_dialect['name']
    if delimiter is None and name is not None and \
            name.lower() == 'csv.excel_tab':
        return '\t'
    return delimiter


def _tableio_optional_args(cfg: ExtractConfig) -> OptionalArgsDict:
    """Get optional TableIO arguments from configuration."""
    csv_dialect = _csv_dialect_name_to_tableio(cfg.out_csv_dialect['name'])
    optional_args: OptionalArgsDict = {
        'character_encoding': cfg.outfile_encoding,
        'csv_delimiter': _csv_delimiter_to_tableio(cfg),
        'csv_quoting': _csv_quoting_to_tableio(cfg.out_csv_dialect['quoting']),
        'csv_quotechar': cfg.out_csv_dialect['quotechar'],
        'csv_lineterminator': cfg.out_csv_dialect['lineterminator'],
        'csv_escapechar': cfg.out_csv_dialect['escapechar'],
    }
    if csv_dialect is not None:
        optional_args['csv_dialect'] = csv_dialect
    return optional_args


def _border_style(cfg: ExtractConfig) -> TableBorderStyle:
    """Get TableIO border style from configuration."""
    if cfg.outfile_border == FormatRequest.NO:
        return TableBorderStyle.NONE
    return TableBorderStyle.OUTER_FIRST_ROW_THICK_INNER_THIN


def _filtered_data_range(cfg: ExtractConfig) -> bool:
    """Return if the output table should request a filtered data range."""
    return cfg.outfile_filtered_area != FormatRequest.NO


def _new_internal_filename(filename: str, extension: str) -> str:
    """Get a new internal output filename and reject existing files."""
    fixed_fname = fix_file_extension(filename=filename, ext_to_add=extension)
    if Path(fixed_fname).exists():
        msg = f'Cowardly refusing to overwrite existing file {fixed_fname}.'
        raise FileExistsError(msg)
    return fixed_fname


def handle_tableio_output(data: Data, filename: str,
                          cfg: ExtractConfig) -> None:
    """Handle output through TableIO."""
    args = _tableio_optional_args(cfg)
    capabilities = get_outfile_capabilities(
        border=cfg.outfile_border, filtered_area=cfg.outfile_filtered_area)
    filtered_args = \
        filter_args_tableio(args=args,
                            format_name=cfg.outfile_type,
                            implementation=cfg.outfile_implementation,
                            capabilities=capabilities)
    with create_tableio(format_name=cfg.outfile_type, file_name=filename,
                        file_access=FileAccess.CREATE, args=filtered_args,
                        implementation=cfg.outfile_implementation,
                        capabilities=capabilities) as table:
        table.write_table_dictdata(
            data=data, column_order=cfg.column_order,
            filtered_data_range=_filtered_data_range(cfg),
            border_style=_border_style(cfg))


def _handle_internal_output(data: Data, filename: str,
                            cfg: ExtractConfig) -> None:
    """Handle internal JSON and XML output formats."""
    if cfg.outfile_type.lower() == 'json':
        fixed_fname = _new_internal_filename(filename=filename,
                                             extension='.json')
        handle_json_output(data=data, filename=fixed_fname, cfg=cfg)
        return
    fixed_fname = _new_internal_filename(filename=filename, extension='.xml')
    handle_xml_output(data=data, filename=fixed_fname, cfg=cfg)


def handle_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Write out data to file in correct format."""
    cfg.validate(stderr_file=sys.stderr)
    if is_internal_out_file_format(cfg.outfile_type):
        _handle_internal_output(data=data, filename=filename, cfg=cfg)
        return
    handle_tableio_output(data=data, filename=filename, cfg=cfg)
