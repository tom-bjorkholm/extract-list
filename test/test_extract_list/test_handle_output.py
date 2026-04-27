#! /usr/local/bin/python3
"""Test printing list."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
from collections.abc import Callable
from typing import cast
import pytest
from config_as_json import JsonType
from tableio import FileAccess, OptionalArgsDict, create_tableio
from extract_list.handle_output import handle_output
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import Data, Value
from extract_list.handle_input import read_in_json, read_in_xml
from .check_capsys import check_capsys


DATA: list[Data] = [
    [{'a': 'ÅÄÖ', 'b': 'cd', 'e': 'fg'},
     {'a': 'åäö', 'b': 'xy', 'e': 'za'}],
    [{'gold': 'Au', 'silver': 'Ag'},
     {'gold': 'Winner', 'silver': 'second'}]
]


def read_txt(filename: str, cfg: ExtractConfig) -> Data:
    """Read from txt file."""
    data: Data = []
    with open(file=filename, mode='r', encoding=cfg.outfile_encoding) as file:
        lines = file.readlines()
        col_names = lines[0].split()
        for row in lines[1:]:
            resrow: dict[str, Value] = {}
            cols = row.split()
            for i, value in enumerate(cols):
                resrow[col_names[i]] = value
            data.append(resrow)
    return data


def read_xml(filename: str, cfg: ExtractConfig) -> Data:
    """Read from XML."""
    indata = read_in_xml(filename=filename, encoding=cfg.outfile_encoding,
                         strip_at=True)
    root = cast(dict[str, dict[str, JsonType]], indata)
    data = cast(Data, list(root['data'].values()))
    return data


def read_json(filename: str, cfg: ExtractConfig) -> Data:
    """Read from JSON."""
    return cast(Data, read_in_json(filename=filename,
                                   encoding=cfg.outfile_encoding))


def read_csv(filename: str, cfg: ExtractConfig) -> Data:
    """Read from CSV."""
    cfg.validate()
    args = cast(OptionalArgsDict,
                {'character_encoding': cfg.outfile_encoding})
    with create_tableio(format_name='CSV', file_name=filename,
                        file_access=FileAccess.READ,
                        implementation='csv', args=args) as table:
        data = table.read_table_dictdata().data
    return data


def read_excel(filename: str, cfg: ExtractConfig) -> Data:
    """Read from Excel."""
    cfg.validate()
    with create_tableio(format_name='Excel', file_name=filename,
                        file_access=FileAccess.READ,
                        implementation='OpenPyXL') as table:
        data = table.read_table_dictdata().data
    return data


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('typ, resfile, reader',
                         [('CSV', 'a.csv', read_csv),
                          ('Excel', 'a.xlsx', read_excel),
                          ('JSON', 'a.json', read_json),
                          ('XML', 'a.xml', read_xml)])
def test_handle_output_ok1(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                           dat: Data, enc: str, typ: str,
                           resfile: str,
                           reader: Callable[[str, ExtractConfig], Data]
                           ) -> None:
    """Test OK cases 1 of handle_output."""
    cfg = ExtractConfig()
    cfg.outfile_encoding = enc
    cfg.outfile_type = typ
    cfg.column_order = list(dat[0].keys())
    cfg.out_xml_attributes = []
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a'
        handle_output(data=dat, filename=fname, cfg=cfg)
        res_fname = dirname + '/' + resfile
        res_data = reader(res_fname, cfg)
        assert res_data == dat
    check_capsys(capsys=capsys)
