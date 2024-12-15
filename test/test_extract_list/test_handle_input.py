#! /usr/local/bin/python3
"""Test input from JSON and as XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from copy import deepcopy
import pytest
import xmltodict
from example_data import ExampleData
from extract_list.handle_json_xml_output import \
    json_output
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import InFileType
from extract_list.handle_input import read_in_json, \
    handle_json_input, strip_prefix_dict, read_in_xml, \
    handle_xml_input, handle_input

# pylint: disable=duplicate-code

DATA = [
    {'data': {'a': 'b', 'c': [2, 3, 4], 'd': 'ÅÄÖåäö'}},
    {'data': {'x': 'y', 'z': True, 'd': [{'a': 'b1'}, {'a': 'c3'}]}}
]


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_read_in_json_ok1(capsys, dat, enc):
    """Test read_in_json."""
    expected = deepcopy(dat)
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        json_output(data=dat, filename=fname, encoding=enc)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == expected
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_read_in_json_ok2(capsys, enc):
    """Test read_in_json."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        txt = '[{"b": "c1"}, {"d": "åäö"}]\n'
        with open(file=fname, mode='w', encoding=enc) as file:
            file.write(txt)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == [{'b': 'c1'}, {'d': 'åäö'}]
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_json_input_ok1(capsys, dat, enc):
    """Test handle_json_input."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    expected = deepcopy(dat)
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        json_output(data=dat, filename=fname, encoding=enc)
        res = handle_json_input(filename=fname, cfg=cfg)
        assert res == expected
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_json_input_ok2(capsys, enc):
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
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('ind, pre, res',
                         [({'a': 'b c', 'abc': 'e f'}, 'ab',
                           {'a': 'b c', 'c': 'e f'}),
                          ([{'ab': 'cd', 'ae': 'fg'},
                            {'ab': 'xy', 'af': 'z'}], 'a',
                           [{'b': 'cd', 'e': 'fg'},
                            {'b': 'xy', 'f': 'z'}]),
                          ({'@a': ['fg', {'@b': 'c', '@g': 'h'}]}, '@',
                           {'a': ['fg', {'b': 'c', 'g': 'h'}]})])
def test_strip_prefix_dict_ok1(capsys, ind, pre, res):
    """Test OK cases for strip_prefix_dict."""
    result = strip_prefix_dict(indata=ind, prefix=pre)
    out, err = capsys.readouterr()
    assert result == res
    assert '' == out
    assert '' == err


XDATA = [
    {'data': {'@a': 'b', 'c': ['2', '3', '4'], 'd': 'ÅÄÖåäö'}},
    {'data': {'@x': 'y', 'z': 'True', 'd': [{'a': 'b1'}, {'a': 'c3'}]}}
]

XDATANOAT = [
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
def test_read_in_xml(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                     enc, ind, at, outd, index):
    """Test read_in_xml."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        outcfg = ExtractConfig()
        outcfg.outfile_encoding = enc
        outcfg.out_xml_attributes = []
        with open(file=fname, mode='w', encoding=enc) as file:
            xmltodict.unparse(input_dict=deepcopy(ind[index]),
                              output=file, encoding=enc,
                              pretty=True)
        result = read_in_xml(filename=fname, encoding=enc, strip_at=at)
    out, err = capsys.readouterr()
    assert result == outd[index]
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('ind, at, outd',
                         [(XDATA, False, XDATA),
                          (XDATA, True, XDATANOAT),
                          (XDATANOAT, True, XDATANOAT),
                          (XDATANOAT, False, XDATANOAT)])
def test_handle_xml_input(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                          enc, ind, at, outd, index):
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
            xmltodict.unparse(input_dict=deepcopy(ind[index]),
                              output=file, encoding=enc,
                              pretty=True)
        result = handle_xml_input(filename=fname, cfg=incfg)
    out, err = capsys.readouterr()
    assert result == outd[index]
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('name', ['a', 'a.xml'])
@pytest.mark.parametrize('ind, at, outd',
                         [(XDATA, False, XDATA),
                          (XDATA, True, XDATANOAT),
                          (XDATANOAT, True, XDATANOAT),
                          (XDATANOAT, False, XDATANOAT)])
def test_handle_input_c_xml(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments, too-many-locals # noqa: E501
                            enc, ind, at, outd, index, name):
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
            xmltodict.unparse(input_dict=deepcopy(ind[index]),
                              output=file, encoding=enc,
                              pretty=True)
        result = handle_input(filename=infname, cfg=incfg)
    out, err = capsys.readouterr()
    assert result == outd[index]
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('name', ['a', 'a.json'])
def test_handle_input_c_json(capsys, dat, enc, name):
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
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_input_c2_json(capsys, enc):
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
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
def test_handle_input_c2_xml(capsys, enc):
    """Test handle_input with xml from ExampleData."""
    cfg = ExtractConfig()
    cfg.infile_encoding = enc
    cfg.infile_type = InFileType.XML
    exdata = ExampleData()
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        exdata.write_xml_to_file(filename=fname, encoding=enc)
        res = handle_input(filename=fname, cfg=cfg)
        expected = {'data': exdata.adjust_for_xml(exdata.data)}
        assert len(res) == len(expected)
        res1 = res['data']
        exp1 = res['data']
        assert len(res1) == len(exp1)
        for key in res1.keys():
            assert res1[key] == exp1[key]
    out, err = capsys.readouterr()
    assert '' == out
    assert '' == err
