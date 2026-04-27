#! /usr/local/bin/python3
"""Test input from JSON and as XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from copy import deepcopy
from typing import cast
import pytest
import xmltodict
from config_as_json import JsonType
from extract_list.handle_json_xml_output import \
    json_output
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import InFileType
from extract_list.handle_input import read_in_json, \
    handle_json_input, strip_prefix_dict, read_in_xml, \
    handle_xml_input, handle_input
from .example_data import ExampleData
from .check_capsys import check_capsys

# pylint: disable=duplicate-code

DATA: list[JsonType] = [
    {'data': {'a': 'b', 'c': [2, 3, 4], 'd': 'ÅÄÖåäö'}},
    {'data': {'x': 'y', 'z': True, 'd': [{'a': 'b1'}, {'a': 'c3'}]}}
]


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_read_in_json_ok1(capsys: pytest.CaptureFixture[str],
                          dat: JsonType, enc: str) -> None:
    """Test read_in_json."""
    expected = deepcopy(dat)
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        json_output(data=dat, filename=fname, encoding=enc)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_read_in_json_ok2(capsys: pytest.CaptureFixture[str],
                          enc: str) -> None:
    """Test read_in_json."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        txt = '[{"b": "c1"}, {"d": "åäö"}]\n'
        with open(file=fname, mode='w', encoding=enc) as file:
            file.write(txt)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == [{'b': 'c1'}, {'d': 'åäö'}]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_json_input_ok1(capsys: pytest.CaptureFixture[str],
                               dat: JsonType, enc: str) -> None:
    """Test handle_json_input."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    expected = deepcopy(dat)
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        json_output(data=dat, filename=fname, encoding=enc)
        res = handle_json_input(filename=fname, cfg=cfg)
        assert res == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_json_input_ok2(capsys: pytest.CaptureFixture[str],
                               enc: str) -> None:
    """Test handle_json_input."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        txt = '[{"b": "c1"}, {"d": "åäö"}]\n'
        with open(file=fname, mode='w', encoding=enc) as file:
            file.write(txt)
        res = handle_json_input(filename=fname, cfg=cfg)
        assert res == [{'b': 'c1'}, {'d': 'åäö'}]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('ind, pre, res',
                         [({'a': 'b c', 'abc': 'e f'}, 'ab',
                           {'a': 'b c', 'c': 'e f'}),
                          ([{'ab': 'cd', 'ae': 'fg'},
                            {'ab': 'xy', 'af': 'z'}], 'a',
                           [{'b': 'cd', 'e': 'fg'},
                            {'b': 'xy', 'f': 'z'}]),
                          ({'@a': ['fg', {'@b': 'c', '@g': 'h'}]}, '@',
                           {'a': ['fg', {'b': 'c', 'g': 'h'}]})])
def test_strip_prefix_dict_ok1(capsys: pytest.CaptureFixture[str],
                               ind: JsonType, pre: str,
                               res: JsonType) -> None:
    """Test OK cases for strip_prefix_dict."""
    result = strip_prefix_dict(indata=ind, prefix=pre)
    assert result == res
    check_capsys(capsys=capsys)


XDATA: list[JsonType] = [
    {'data': {'@a': 'b', 'c': ['2', '3', '4'], 'd': 'ÅÄÖåäö'}},
    {'data': {'@x': 'y', 'z': 'True', 'd': [{'a': 'b1'}, {'a': 'c3'}]}}
]

XDATANOAT: list[JsonType] = [
    {'data': {'a': 'b', 'c': ['2', '3', '4'], 'd': 'ÅÄÖåäö'}},
    {'data': {'x': 'y', 'z': 'True', 'd': [{'a': 'b1'}, {'a': 'c3'}]}}
]


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('ind, at, outd',
                         [(XDATA, False, XDATA),
                          (XDATA, True, XDATANOAT),
                          (XDATANOAT, True, XDATANOAT),
                          (XDATANOAT, False, XDATANOAT)])
def test_read_in_xml(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                     enc: str, ind: list[JsonType], at: bool,
                     outd: list[JsonType], index: int) -> None:
    """Test read_in_xml."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        outcfg = ExtractConfig()
        outcfg.outfile_encoding = enc
        outcfg.out_xml_attributes = []
        with open(file=fname, mode='w', encoding=enc) as file:
            input_dict = cast(dict[str, JsonType], deepcopy(ind[index]))
            xmltodict.unparse(input_dict=input_dict,
                              output=file, encoding=enc,
                              pretty=True)
        result = read_in_xml(filename=fname, encoding=enc, strip_at=at)
    assert result == outd[index]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('ind, at, outd',
                         [(XDATA, False, XDATA),
                          (XDATA, True, XDATANOAT),
                          (XDATANOAT, True, XDATANOAT),
                          (XDATANOAT, False, XDATANOAT)])
def test_handle_xml_input(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                          enc: str, ind: list[JsonType], at: bool,
                          outd: list[JsonType], index: int) -> None:
    """Test handle_xml_input."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        outcfg = ExtractConfig()
        outcfg.outfile_encoding = enc
        outcfg.out_xml_attributes = []
        incfg = ExtractConfig()
        incfg.infile_encoding = enc
        incfg.in_xml_strip_at = at
        with open(file=fname, mode='w', encoding=enc) as file:
            input_dict = cast(dict[str, JsonType], deepcopy(ind[index]))
            xmltodict.unparse(input_dict=input_dict,
                              output=file, encoding=enc,
                              pretty=True)
        result = handle_xml_input(filename=fname, cfg=incfg)
    assert result == outd[index]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('name', ['a', 'a.xml'])
@pytest.mark.parametrize('ind, at, outd',
                         [(XDATA, False, XDATA),
                          (XDATA, True, XDATANOAT),
                          (XDATANOAT, True, XDATANOAT),
                          (XDATANOAT, False, XDATANOAT)])
def test_handle_input_c_xml(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments, too-many-locals # noqa: E501
                            enc: str, ind: list[JsonType], at: bool,
                            outd: list[JsonType], index: int,
                            name: str) -> None:
    """Test handle_input for xml."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        outcfg = ExtractConfig()
        outcfg.outfile_encoding = enc
        outcfg.out_xml_attributes = []
        incfg = ExtractConfig()
        incfg.infile_type = InFileType.XML
        incfg.infile_encoding = enc
        incfg.in_xml_strip_at = at
        infname = dirname + '/' + name
        with open(file=fname, mode='w', encoding=enc) as file:
            input_dict = cast(dict[str, JsonType], deepcopy(ind[index]))
            xmltodict.unparse(input_dict=input_dict,
                              output=file, encoding=enc,
                              pretty=True)
        result = handle_input(filename=infname, cfg=incfg)
    assert result == outd[index]
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('name', ['a', 'a.json'])
def test_handle_input_c_json(capsys: pytest.CaptureFixture[str],
                             dat: JsonType, enc: str, name: str) -> None:
    """Test handle_input for json."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    cfg.infile_type = InFileType.JSON
    expected = deepcopy(dat)
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        infname = dirname + '/' + name
        json_output(data=dat, filename=fname, encoding=enc)
        res = handle_input(filename=infname, cfg=cfg)
        assert res == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_input_c2_json(capsys: pytest.CaptureFixture[str],
                              enc: str) -> None:
    """Test handle_input with json from ExampleData."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    cfg.infile_type = InFileType.JSON
    exdata = ExampleData()
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        exdata.write_json_to_file(filename=fname, encoding=enc)
        res = handle_input(filename=fname, cfg=cfg)
        assert res == exdata.data
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_input_c2_xml(capsys: pytest.CaptureFixture[str],
                             enc: str) -> None:
    """Test handle_input with xml from ExampleData."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    cfg.infile_type = InFileType.XML
    exdata = ExampleData()
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        exdata.write_xml_to_file(filename=fname, encoding=enc)
        res = handle_input(filename=fname, cfg=cfg)
        expected = read_in_xml(filename=fname, encoding=enc, strip_at=False)
        assert res == expected
    check_capsys(capsys=capsys)
