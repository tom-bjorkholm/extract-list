#! /usr/local/bin/python3
"""Test variations of configuration file for extract list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

# import sys
# from tempfile import TemporaryDirectory
from copy import deepcopy
# from enum import Enum, auto
import pytest
from check_cfgs_equal import check_cfgs_equal
from extract_list.config_enums import InFileType, OutFileType
from extract_list.extract_config import ExtractConfig


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         [OutFileType.JSON, OutFileType.XML, OutFileType.CSV,
                          OutFileType.EXCEL, OutFileType.TXT])
def test_extract_config_var1(capsys, inenc, infiletype, outenc, outfiletype):
    """Test variation 1 of  configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.outfile_encoding = deepcopy(outenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.outfile_type = deepcopy(outfiletype)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    check_cfgs_equal(cfg, cf2)
    assert cf2.infile_type == infiletype
    assert cf2.infile_encoding == inenc
    assert cf2.outfile_type == outfiletype
    assert cf2.outfile_encoding == outenc
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


# TODO test variations of valid configuraitons
# TODO test messages for variations of invalid configurations
