#! /usr/local/bin/python3
"""Generate example configuration for extracting a list from JSON or XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

# from typing import TextIO
from enum import Enum
import sys
from excel_list_transform.str_to_enum import string_to_enum_best_match
from excel_list_transform.file_extension import fix_file_extension
from extract_list.config_enums import OutFileType, InFileType
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt import generate_txt_nyi


def generate_cfg_example(outfilename: str, cfgtype: CfgTypes,
                         outtype: OutFileType) -> int:
    """Generate cfg file for example."""
    assert cfgtype in (CfgTypes.EXAMPLE_JSON, CfgTypes.EXAMPLE_XML)
    cfg = ExtractConfig()
    cfg.outfile_type = outtype
    if cfgtype == CfgTypes.EXAMPLE_JSON:
        cfg.infile_type = InFileType.JSON
    else:  # XML
        cfg.infile_type = InFileType.XML
        cfg.main_line.line.insert(0, 'data')
        cfg.linked_lines[0].line.insert(0, 'data')
    cfg.write(to_json_filename=outfilename)
    return 0


def generate_cfg_nyi(outfilename: str, cfgtype: CfgTypes,
                     outtype: OutFileType) -> int:
    """Inform of for not yet implemented function."""
    print("Sorry. Generation of example config file not yet implemented,",
          file=sys.stderr)
    with open(file=outfilename, mode='wt', encoding='utf-8') as file:
        print("Sorry. Generation of example config file not yet implemented,",
              file=file)
    assert isinstance(cfgtype, CfgTypes)
    assert isinstance(outtype, OutFileType)
    return 1


def _lower_str_enum(etype: type[Enum]) -> list[str]:
    """Get a lower case list of strings for enum."""
    return [e.name.lower() for e in etype]


def get_types_of_cfg() -> list[str]:
    """Get a list of possible example configurations."""
    return _lower_str_enum(CfgTypes)


def get_out_file_types() -> list[str]:
    """Get a list of possible out file types in config."""
    return _lower_str_enum(OutFileType)


TXTFUNCS = {CfgTypes.EXAMPLE_JSON: generate_txt_nyi,
            CfgTypes.EXAMPLE_XML: generate_txt_nyi,
            CfgTypes.SW_JSON_TO_RRS: generate_txt_nyi,
            CfgTypes.SW_XML_TO_RRS: generate_txt_nyi}

CFGFUNCS = {CfgTypes.EXAMPLE_JSON: generate_cfg_example,
            CfgTypes.EXAMPLE_XML: generate_cfg_example,
            CfgTypes.SW_JSON_TO_RRS: generate_cfg_nyi,
            CfgTypes.SW_XML_TO_RRS: generate_cfg_nyi}


def generate_example_cfg(filename: str, cfgtype: str,
                         out_file_type: str) -> int:
    """Generate example configuration file and accompanying txt file."""
    type_of_cfg = string_to_enum_best_match(inp=cfgtype, num_type=CfgTypes)
    type_out = string_to_enum_best_match(inp=out_file_type,
                                         num_type=OutFileType)
    cfgout = fix_file_extension(filename=filename, ext_to_add='.cfg')
    ret = CFGFUNCS[type_of_cfg](outfilename=cfgout, cfgtype=type_of_cfg,
                                outtype=type_out)
    if ret != 0:
        return ret
    txtout = fix_file_extension(filename=filename, ext_to_add='.txt',
                                ext_to_remove='.cfg')
    with open(file=txtout, mode='wt', encoding='utf-8') as file:
        ret = TXTFUNCS[type_of_cfg](file=file, cfgtype=type_of_cfg,
                                    outtype=type_out)
        return ret
