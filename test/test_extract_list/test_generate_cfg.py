#! /usr/local/bin/python3
"""Test generation of example configuration."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from json import loads as json_loads
from shutil import copyfile
from collections.abc import Callable
from typing import Optional, cast
import pytest
from config_as_json.file_extension import fix_file_extension
from extract_list.generate_cfg import generate_cfg_example, \
    generate_cfg_example2, generate_cfg_sw_to_rrs
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import CfgTypes, Data
from extract_list.extract_func import extract_func
from extract_list.extract_cmd import extract_cmd
from .example_data import ExampleData
from .test_handle_output import read_csv, read_excel, \
    read_json
from .check_capsys import check_capsys
from .check_result import check_result, ex_res, ex2_res


def assert_cfg_text_output(cfgtxt: str, output_format: str) -> None:
    """Check that configuration JSON selects the expected output format."""
    expected = '"format_name": "' + output_format + '"'
    assert expected.lower() in cfgtxt.lower()


@pytest.mark.parametrize('outp',
                         [('Excel', read_excel,
                           'b.xlsx'),
                          ('CSV', read_csv,
                           'b.csv'),
                          ('JSON', read_json,
                           'b.json')])
@pytest.mark.parametrize('inp',
                         [(CfgTypes.EXAMPLE_JSON,
                           ExampleData.write_json_to_file,
                           'a.json', ex_res, generate_cfg_example),
                          (CfgTypes.EXAMPLE_XML,
                           ExampleData.write_xml_to_file,
                           'a.xml', ex_res, generate_cfg_example),
                          (CfgTypes.EXAMPLE2_JSON,
                           ExampleData.write_json_to_file,
                           'd.json', ex2_res, generate_cfg_example2),
                          (CfgTypes.EXAMPLE2_XML,
                           ExampleData.write_xml_to_file,
                           'd.xml', ex2_res, generate_cfg_example2)])
def test_gen_cfg_ex_ok1(capsys: pytest.CaptureFixture[str],
                        outp: tuple[str,
                                    Callable[[str, ExtractConfig], Data],
                                    str],
                        inp: tuple[CfgTypes,
                                   Callable[[ExampleData, str], None],
                                   str, Data,
                                   Callable[[str, CfgTypes, str],
                                            int]]) -> None:
    """Test OK cases 1 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        example = ExampleData()
        inp[1](example, in_fname)
        ret = inp[4](cfg_fname, inp[0], outp[0])
        ret2 = extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                            out_file_name=out_fname)
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](out_fname, cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data, other_result=inp[3])
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read()
            assert_cfg_text_output(cfgtxt=cfgtxt, output_format=outp[0])
    check_capsys(capsys=capsys)


sw_res_data: Data = [
    {'Class': 'Dragon', 'Division': 'b-div', 'Nationality': 'CAN',
     'Sail Number': '456', 'Boat Name': 'Molly', 'Name': 'Mickey Mouse',
     'Club Name': 'DEF',
     'Email': 'm.mouse@icloud.com.can', 'Phone': '+1555234567'},
    {'Class': 'Optimist', 'Division': 'y-div', 'Nationality': 'USA',
     'Sail Number': '123', 'Boat Name': 'Sally', 'Name': 'Donald Duck',
     'Club Name': 'ABC',
     'Email': 'd.duck@gmail.com.us', 'Phone': '+1555123456'}
]


@pytest.mark.parametrize('outp',
                         [('Excel', read_excel,
                           'b.xlsx'),
                          ('CSV', read_csv,
                           'b.csv'),
                          ('JSON', read_json,
                           'b.json')])
@pytest.mark.parametrize('inp',
                         [(CfgTypes.SW_JSON_TO_RRS,
                           'test/test_extract_list/SW.json',
                           'a.json'),
                          (CfgTypes.SW_XML_TO_RRS,
                           'test/test_extract_list/SW.xml',
                           'a.xml')])
def test_gen_cfg_sw_ok1(capsys: pytest.CaptureFixture[str],
                        outp: tuple[str,
                                    Callable[[str, ExtractConfig], Data],
                                    str],
                        inp: tuple[CfgTypes, str, str]) -> None:
    """Test OK cases 1 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        copyfile(src=inp[1], dst=in_fname)
        ret = generate_cfg_sw_to_rrs(outfilename=cfg_fname, cfgtype=inp[0],
                                     outtype=outp[0])
        ret2 = extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                            out_file_name=out_fname)
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](out_fname, cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data, other_result=sw_res_data)
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read()
            assert_cfg_text_output(cfgtxt=cfgtxt, output_format=outp[0])
    check_capsys(capsys=capsys)


def check_txt_file_for_cfg(cfg_fname: str,
                           othermsgs: Optional[list[str]] = None) -> None:
    """Check that text file for cfg file has all information."""
    txt_fname = fix_file_extension(filename=cfg_fname, ext_to_add='.txt',
                                   ext_to_remove='.cfg', for_reading=False)
    cfg = ExtractConfig(from_json_filename=cfg_fname)
    cfg_data = cast(dict[str, object], json_loads(cfg.as_json_string()))
    num_keys_checked = 0
    with open(file=txt_fname, mode='r', encoding='utf-8') as file:
        txt = file.read()
        for key in cfg_data.keys():
            match_txt = '"' + key + '"'
            assert match_txt in txt
            num_keys_checked += 1
        if othermsgs is not None:
            for msg in othermsgs:
                assert msg in txt
    assert num_keys_checked > 10


@pytest.mark.parametrize('outp',
                         [('excel', read_excel,
                           'b.xlsx'),
                          ('csv', read_csv,
                           'b.csv')])
@pytest.mark.parametrize('inp',
                         [('sw_json_to_rrs',
                           'test/test_extract_list/SW.json',
                           'a.json'),
                          ('sw_xml_to_rrs',
                           'test/test_extract_list/SW.xml',
                           'a.xml')])
def test_gen_cfg_sw_ok2(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-locals # noqa: E501
                        outp: tuple[str,
                                    Callable[[str, ExtractConfig], Data],
                                    str],
                        inp: tuple[str, str, str]) -> None:
    """Test OK cases 2 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        copyfile(src=inp[1], dst=in_fname)
        gen_cmd = ['cfg-example', '-k', inp[0], '-t', outp[0],
                   '-o', cfg_fname]
        ret = extract_cmd(gen_cmd)
        extr_cmd = ['extract', '-i', in_fname, '-o', out_fname,
                    '-c', cfg_fname]
        ret2 = extract_cmd(extr_cmd)
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read().lower()
            assert_cfg_text_output(cfgtxt=cfgtxt, output_format=outp[0])
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](out_fname, cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data, other_result=sw_res_data)
        check_txt_file_for_cfg(cfg_fname=cfg_fname)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('outp',
                         [('json', read_json,
                           'b.json')])
@pytest.mark.parametrize('inp',
                         [('sw_json_to_rrs',
                           'test/test_extract_list/SW.json',
                           'a.json'),
                          ('sw_xml_to_rrs',
                           'test/test_extract_list/SW.xml',
                           'a.xml')])
def test_gen_cfg_sw_warn(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-locals # noqa: E501
                         outp: tuple[str,
                                     Callable[[str, ExtractConfig], Data],
                                     str],
                         inp: tuple[str, str, str]) -> None:
    """Test OK cases of generate cfg exmaple with warnings."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        copyfile(src=inp[1], dst=in_fname)
        gen_cmd = ['cfg-example', '-k', inp[0], '-t', outp[0],
                   '-o', cfg_fname]
        ret = extract_cmd(gen_cmd)
        extr_cmd = ['extract', '-i', in_fname, '-o', out_fname,
                    '-c', cfg_fname]
        ret2 = extract_cmd(extr_cmd)
        notice_msgs = [
            'Notice: The expected next step excel-list-transform',
            'will require input in excel or CSV format!',
            'But the selected output type is:'
        ]
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read().lower()
            assert_cfg_text_output(cfgtxt=cfgtxt, output_format=outp[0])
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](out_fname, cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data, other_result=sw_res_data)
        check_txt_file_for_cfg(cfg_fname=cfg_fname, othermsgs=notice_msgs)
    check_capsys(capsys=capsys, in_err=notice_msgs)


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
                           'a.json', ex_res),
                          ('example_xml',
                           ExampleData.write_xml_to_file,
                           'a.xml', ex_res),
                          ('example2_json',
                           ExampleData.write_json_to_file,
                           'd.json', ex2_res),
                          ('example2_xml',
                           ExampleData.write_xml_to_file,
                           'd.xml', ex2_res)])
def test_gen_cfg_ex_ok2(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-locals # noqa: E501
                        outp: tuple[str,
                                    Callable[[str, ExtractConfig], Data],
                                    str],
                        inp: tuple[str, Callable[[ExampleData, str], None],
                                   str, Data]) -> None:
    """Test OK cases 2 of generate cfg exmaple."""
    with TemporaryDirectory() as folder:
        out_fname = folder + '/' + outp[2]
        in_fname = folder + '/' + inp[2]
        cfg_fname = folder + '/' + 'c.cfg'
        example = ExampleData()
        inp[1](example, in_fname)
        gen_cmd = ['cfg-example', '-k', inp[0], '-t', outp[0],
                   '-o', cfg_fname]
        ret = extract_cmd(gen_cmd)
        extr_cmd = ['extract', '-i', in_fname, '-o', out_fname,
                    '-c', cfg_fname]
        ret2 = extract_cmd(extr_cmd)
        with open(file=cfg_fname, mode='r', encoding='utf-8') as file:
            cfgtxt = file.read().lower()
            assert_cfg_text_output(cfgtxt=cfgtxt, output_format=outp[0])
        cfg = ExtractConfig(from_json_filename=cfg_fname)
        data = outp[1](out_fname, cfg)
        assert ret == 0
        assert ret2 == 0
        check_result(result_data=data, other_result=inp[3])
        check_txt_file_for_cfg(cfg_fname=cfg_fname)
    check_capsys(capsys=capsys)
