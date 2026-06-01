#! /usr/local/bin/python3
"""Produce output to file in chosen format."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

import sys
from pathlib import Path
from config_as_json.file_extension import fix_file_extension
from tableio import FileAccess, TableBorderStyle, tio_config_create
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import Data
from extract_list.config_enums import FormatRequest, \
    get_outfile_capabilities, is_internal_out_file_format
from extract_list.handle_json_xml_output import \
    handle_json_output, handle_xml_output
from extract_list.handle_txt_output import handle_txt_output


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
    capabilities = get_outfile_capabilities(
        border=cfg.outfile_border, filtered_area=cfg.outfile_filtered_area)
    with tio_config_create(config=cfg.output, file_name=filename,
                           file_access=FileAccess.CREATE,
                           capabilities=capabilities) as table:
        table.write_table_dictdata(
            data=data, column_order=cfg.column_order,
            filtered_data_range=_filtered_data_range(cfg),
            border_style=_border_style(cfg))


def _handle_internal_output(data: Data, filename: str,
                            cfg: ExtractConfig) -> None:
    """Handle internal output formats."""
    output_format = cfg.output.format_name.lower()
    if output_format == 'json':
        fixed_fname = _new_internal_filename(filename=filename,
                                             extension='.json')
        handle_json_output(data=data, filename=fixed_fname, cfg=cfg)
        return
    if output_format == 'plaintxt':
        fixed_fname = _new_internal_filename(filename=filename,
                                             extension='.txt')
        handle_txt_output(data=data, filename=fixed_fname, cfg=cfg)
        return
    fixed_fname = _new_internal_filename(filename=filename, extension='.xml')
    handle_xml_output(data=data, filename=fixed_fname, cfg=cfg)


def handle_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Write out data to file in correct format."""
    cfg.validate(stderr_file=sys.stderr)
    if is_internal_out_file_format(cfg.output.format_name):
        _handle_internal_output(data=data, filename=filename, cfg=cfg)
        return
    handle_tableio_output(data=data, filename=filename, cfg=cfg)
