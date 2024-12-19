#! /usr/local/bin/python3
"""Generate text describing example configuration."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import TextIO
import sys
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes


def generate_txt_nyi(file: TextIO, cfgtype: CfgTypes,
                     outtype: OutFileType) -> int:
    """Inform of not yet implemented function."""
    print("Sorry. Generation of example text file not yet implemented,",
          file=sys.stderr)
    print("Sorry. Generation of example text file not yet implemented,",
          file=file)
    assert isinstance(cfgtype, CfgTypes)
    assert isinstance(outtype, OutFileType)
    return 1
