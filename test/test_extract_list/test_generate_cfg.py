#! /usr/local/bin/python3
"""Test generation of example configuration."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
import pytest
from example_data import ExampleData
from test_handle_output import read_csv, read_excel, read_json
from check_capsys import check_capsys
from check_result import check_result
from extract_list.generate_cfg import generate_cfg_example
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes
from extract_list.extract_func import extract_func
from extract_list.extract_cmd import extract_cmd


@pytest.mark.parametrize('outp',
                         [(OutFileType.EXCEL, read_excel,
                           'b.xlsx'),
                          (OutFileType.CSV, read_csv,
                           'b.csv'),
                          (OutFileType.JSON, read_json,
                           'b.json')])
@pytest.mark.parametrize('inp',
                         [(CfgTypes.EXAMPLE_JSON,
                           ExampleData.write_json_to_file,
                           'a.json'),
                          (CfgTypes.EXAMPLE_XML,
                           ExampleData.write_xml_to_file,
                           'a.xml')])
def test_gen_cfg_ex_ok1(capsys, outp, inp):
    """Test OK cases 1 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        example = ExampleData()
        inp[1](example, filename=in_fname)
        ret = generate_cfg_example(outfilename=cfg_fname,
                                   cfgtype=inp[0],
                                   outtype=outp[0])
        ret2 = extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                            out_file_name=out_fname)
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](filename=out_fname, cfg=cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data)
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read()
            assert '"outfile_type": "' + outp[0].name + '"' in cfgtxt
    check_capsys(capsys=capsys)


# TODO  This test requires generate txt to be implemented
@pytest.mark.skip
@pytest.mark.parametrize('outp',
                         [('excel', read_excel,
                           'b.xlsx'),
                          ('csv', read_csv,
                           'b.csv'),
                          ('json', read_json,
                           'b.json')])
@pytest.mark.parametrize('inp',
                         [('example_json',
                           ExampleData.write_json_to_file,
                           'a.json'),
                          ('example_xml',
                           ExampleData.write_xml_to_file,
                           'a.xml')])
def test_gen_cfg_ex_ok2(capsys,  # pylint: disable=too-many-locals
                        outp, inp):
    """Test OK cases 2 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        example = ExampleData()
        inp[1](example, filename=in_fname)
        gen_cmd = ['cfg-example', '-k', inp[0], '-t', outp[0],
                   '-o', cfg_fname]
        ret = extract_cmd(gen_cmd)
        extr_cmd = ['extract', '-i', in_fname, '-o', out_fname,
                    '-c', cfg_fname]
        ret2 = extract_cmd(extr_cmd)
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](filename=out_fname, cfg=cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data)
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read()
            assert '"outfile_type": "' + outp[0].name + '"' in cfgtxt
    check_capsys(capsys=capsys)
