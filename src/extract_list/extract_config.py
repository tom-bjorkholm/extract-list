#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import Optional
from excel_list_transform.config import Config
from excel_list_transform.config_enums import ExcelLib
from extract_list.config_enums import InFileType, OutFileType


class ExtractConfig(Config):
    """Configuration of extract a list of columns from JSON or XML."""

    def __init__(self,  from_json_data_text: Optional[str],
                 from_json_filename: Optional[str]) -> None:
        """Construct extract configuration object."""
        self.infile_type: InFileType = InFileType.JSON
        self.infile_encoding: str = 'utf-8'
        self.outfile_type: OutFileType = OutFileType.EXCEL
        self.outfile_encoding: str = 'utf-8'
        self.out_excel_library: ExcelLib = ExcelLib.PYLIGHTXL
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number']
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename)
        # do checking
