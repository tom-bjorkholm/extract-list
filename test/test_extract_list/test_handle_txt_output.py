#! /usr/local/bin/python3
"""Test printing list of dicts as table in text."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from typing import Optional
import pytest
from extract_list.handle_txt_output import handle_txt_output, print_col
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import Data
from .check_capsys import check_capsys


@pytest.mark.parametrize('txt, length',
                         [('hi', 10), ('Donald Duck', 20),
                          ('Hello', 5)])
def test_print_col_ok(capsys: pytest.CaptureFixture[str], txt: str,
                      length: int) -> None:
    """Test OK test cases for print_col."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.txt'
        with open(file=fname, mode='w', encoding='utf-8') as file:
            print_col(file=file, item=txt, width=length)
        with open(file=fname, mode='r', encoding='utf-8') as file:
            res = file.readline()
            assert len(res) == length
            assert res.strip() == txt
    check_capsys(capsys=capsys)


def column_starts(line: str) -> list[int]:
    """Get start position of each column."""
    space = True
    ret: list[int] = []
    for pos, char in enumerate(line):
        if space != char.isspace():
            space = char.isspace()
            if not space:
                ret.append(pos)
    ret.append(len(line))
    return ret


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('data, cols, res',
                         [([{'a': 'Hello', 'b': 'world'},
                            {'a': 'beautiful', 'b': 'ö'}],
                           ['b', 'a'],
                           [['b', 'a'],
                            ['world', 'Hello'],
                            ['ö', 'beautiful']]),
                          ([], ['Some', 'columns'],
                           [['Some', 'columns']]),
                          ([{'a': 'Hello', 'b': 'world', 'long': 'a'},
                            {'a': 'beautiful', 'b': 'ö', 'long': 'å'}],
                           ['long'],
                           [['long'], ['a'], ['å']])])
def test_handle_txt_output(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-locals # noqa: E501
                           data: Data, cols: list[str],
                           res: list[list[str]], enc: str) -> None:
    """Test OK test cases for handle_txt_output."""
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a.txt'
        cfg = ExtractConfig()
        cfg.outfile_encoding = enc
        cfg.column_order = cols
        handle_txt_output(data=data, filename=fname, cfg=cfg)
        with open(file=fname, mode='r', encoding=enc) as file:
            prev_col_start: Optional[list[int]] = None
            result: list[list[str]] = []
            lines = file.readlines()
            for row in lines:
                col_start = column_starts(row)
                if prev_col_start is None:
                    prev_col_start = col_start
                else:
                    assert prev_col_start == col_start
                result.append(row.split())
            assert res == result
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('cols', [['a', 'b'], ['c', 'd', 'e']])
@pytest.mark.parametrize('fname', ['a.txt', 'b.dat'])
@pytest.mark.parametrize('dat', [[{'a': 'h', 'b': 'i'}], []])
def test_handle_txt_output2(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-positional-arguments,too-many-arguments # noqa: E501
                            monkeypatch: pytest.MonkeyPatch, enc: str,
                            cols: list[str], fname: str, dat: Data) -> None:
    """Tested mocked test cases for handle_txt_output."""
    count = 0

    def mocktxtout(data: Data, column_order: list[str], filename: str,
                   encoding: str) -> None:
        """Mock txt_output."""
        nonlocal count
        count += 1
        assert data == dat
        assert column_order == cols
        assert filename == fname
        assert encoding == enc

    monkeypatch.setattr('extract_list.handle_txt_output.txt_output',
                        mocktxtout)
    cfg = ExtractConfig()
    cfg.outfile_encoding = enc
    cfg.column_order = cols
    handle_txt_output(data=dat, filename=fname, cfg=cfg)
    assert count == 1
    check_capsys(capsys=capsys)
