#! /usr/local/bin/python3
"""Test printing list of dicts as JSON and as XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from copy import deepcopy
from typing import Optional
import pytest
from config_as_json import JsonType
from extract_list.handle_json_xml_output import \
    json_output, handle_json_output, append_to_key, handle_xml_output
from extract_list.extract_config import ExtractConfig
from extract_list.handle_input import read_in_json, read_in_xml
from extract_list.commontypes import Data, Row
from .check_capsys import check_capsys


# pylint: disable=duplicate-code


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('data',
                         [{'foo': ['abc', 'ÅÄÖ']},
                          {'abc': {'def': 45, 'ge': False,
                                   'hj': None, 'kl': [1, 2, 3]}},
                          [{'ab': 4, 'cd': 'hello'},
                           {'ab': 42, 'cd': 'goodbye'}]])
def test_json_output_ok1(capsys: pytest.CaptureFixture[str], data: JsonType,
                         enc: str) -> None:
    """Test 1 of json_output."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        json_output(data=data, filename=fname, encoding=enc)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == data
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('data',
                         [{'foo': ['abc', 'ÅÄÖ']},
                          {'abc': {'def': 45, 'ge': False,
                                   'hj': None, 'kl': [1, 2, 3]}},
                          [{'ab': 4, 'cd': 'hello'},
                           {'ab': 42, 'cd': 'goodbye'}]])
def test_json_output_ok2(capsys: pytest.CaptureFixture[str], data: JsonType,
                         enc: str) -> None:
    """Test 2 of json_output."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.json'
        cfg = ExtractConfig()
        cfg.set_output_format('JSON')
        cfg.internal_output_encoding = enc
        handle_json_output(data=data, filename=fname, cfg=cfg)
        res = read_in_json(filename=fname, encoding=enc)
        assert res == data
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('dat',
                         [{'foo': ['abc', 'ÅÄÖ']},
                          {'abc': {'def': 45, 'ge': False,
                                   'hj': None, 'kl': [1, 2, 3]}},
                          [{'ab': 4, 'cd': 'hello'},
                           {'ab': 42, 'cd': 'goodbye'}]])
@pytest.mark.parametrize('fname', ['/tmp/a.b.json', '/tmp/c/d.json'])
def test_json_output_ok3(capsys: pytest.CaptureFixture[str],
                         monkeypatch: pytest.MonkeyPatch, dat: JsonType,
                         enc: str, fname: str) -> None:
    """Test 3 of json_output."""
    cfg = ExtractConfig()
    cfg.set_output_format('JSON')
    cfg.internal_output_encoding = enc

    count = 0

    def mock_j_out(data: Data | JsonType, filename: str,
                   encoding: str) -> None:
        """Mock of json_output."""
        nonlocal count
        count += 1
        assert data == dat
        assert filename == fname
        assert encoding == enc
    monkeypatch.setattr('extract_list.handle_json_xml_output.json_output',
                        mock_j_out)
    handle_json_output(data=dat, filename=fname, cfg=cfg)
    assert count == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('row, key, pre, res',
                         [({'ab': 4, 'cd': 'ef'}, 'cd', 'xy',
                           {'ab': 4, 'xycd': 'ef'}),
                          ({'ab': 4, 'cd': 'ef', 'gh': True}, 'cd', '@',
                           {'ab': 4, '@cd': 'ef', 'gh': True}),
                          ({'ab': 4, 'cd': 'ef'}, 'ab', '12',
                           {'12ab': 4, 'cd': 'ef'})])
def test_append_to_key_ok(capsys: pytest.CaptureFixture[str], row: Row,
                          key: str, pre: str, res: Row) -> None:
    """Test OK cases of append_to_key."""
    rowarg = deepcopy(row)
    append_to_key(row=rowarg, key=key, prefix=pre)
    assert rowarg == res
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf8', 'iso8859-1'])
@pytest.mark.parametrize('dat, attr, key, res',
                         [([{'a': 'b', 'c': 2, 'd': 'e'},
                            {'a': 'x', 'c': 7, 'd': 'y'}], ['d'], None,
                           {'data': {'row_0': {'a': 'b', 'c': '2',
                                               '@d': 'e'},
                                     'row_1': {'a': 'x', 'c': '7',
                                               '@d': 'y'}}}),
                          ([{'a': 'b', 'c': '2', 'd': 'e'},
                            {'a': 'xåäö', 'c': '7', 'd': 'y'}], ['c'], None,
                           {'data': {'row_0': {'a': 'b', '@c': '2',
                                               'd': 'e'},
                                     'row_1': {'a': 'xåäö', '@c': '7',
                                               'd': 'y'}}}),
                          ([{'a': 'b', 'c': 2, 'd': 'e'},
                            {'a': 'x', 'c': 7, 'd': 'y'}], ['d'], 'a',
                           {'data': {'b': {'a': 'b', 'c': '2', '@d': 'e'},
                                     'x': {'a': 'x', 'c': '7', '@d': 'y'}}})
                          ])
# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def test_xml_output_1(capsys: pytest.CaptureFixture[str], enc: str, dat: Data,
                      attr: list[str], key: Optional[str], res: JsonType) \
                          -> None:
    """Test xml output in first way."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.xml'
        cfg = ExtractConfig()
        cfg.out_xml_attributes = attr
        cfg.set_output_format('XML')
        cfg.internal_output_encoding = enc
        cfg.include_key = key is not None
        if key is not None:
            cfg.column_name_for_key = key
        handle_xml_output(data=dat, filename=fname, cfg=cfg)
        result = read_in_xml(filename=fname, encoding=enc, strip_at=False)
    assert result == res
    check_capsys(capsys=capsys)


def dict_add(thedict: dict[str, list[str]], dictkey: str, addtxt: str) -> None:
    """Add key and text to dict."""
    if dictkey not in thedict:
        thedict[dictkey] = [addtxt]
    else:
        thedict[dictkey].append(addtxt)


@pytest.mark.parametrize('enc', ['utf8', 'iso8859-1'])
@pytest.mark.parametrize('dat, key, res',
                         [([{'a': 'b', 'c': 2, 'd': 'e'},
                            {'a': 'x', 'c': 7, 'd': 'y'}], None,
                           {'data': {'row_0': {'a': 'b', 'c': 2,
                                               'd': 'e'},
                                     'row_1': {'a': 'x', 'c': 7,
                                               'd': 'y'}}}),
                          ([{'a': 'b', 'c': 2, 'd': 'e'},
                            {'a': 'x', 'c': 7, 'd': 'y'}], 'a',
                           {'data': {'b': {'a': 'b', 'c': 2, 'd': 'e'},
                                     'x': {'a': 'x', 'c': 7, 'd': 'y'}}})])
@pytest.mark.parametrize('attr', [[], ['a'], ['a', 'd']])
# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def test_xml_output_2(capsys: pytest.CaptureFixture[str],
                      monkeypatch: pytest.MonkeyPatch, enc: str, dat: Data,
                      attr: list[str], key: Optional[str],
                      res: JsonType) -> None:
    """Test xml output with mocking."""
    calls: dict[str, list[str]] = {}

    def mock_key_append(row: Row, key: str, prefix: str) -> None:
        """Mock append_to_key."""
        dict_add(calls, prefix, key)
        assert row in dat

    count = 0

    def mock_unparse(data: JsonType, output: object, pretty: bool = False,
                     encoding: Optional[str] = None) -> None:
        """Mock xmltodict.unparse."""
        nonlocal count
        count += 1
        assert pretty
        assert data == res
        assert encoding == enc
        assert output is not None
    monkeypatch.setattr('extract_list.handle_json_xml_output.append_to_key',
                        mock_key_append)
    unparse = 'extract_list.handle_json_xml_output.xmltodict.unparse'
    monkeypatch.setattr(unparse, mock_unparse)
    cfg = ExtractConfig()
    cfg.set_output_format('XML')
    cfg.internal_output_encoding = enc
    cfg.include_key = key is not None
    if key is not None:
        cfg.column_name_for_key = key
    cfg.out_xml_attributes = attr
    handle_xml_output(data=dat, filename='/tmp/a.xml', cfg=cfg)
    assert count == 1
    if len(attr) != 0:
        assert len(calls) == 1
        assert '@' in calls
        cattr: list[str] = []
        for _ in dat:
            cattr += attr
        assert cattr == calls['@']
    else:
        assert len(calls) == 0
    check_capsys(capsys=capsys)
