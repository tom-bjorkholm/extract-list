#! /usr/local/bin/python3
"""Test printing list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from tempfile import TemporaryDirectory
import pytest
from check_capsys import check_capsys
from excel_list_transform.handle_csv import read_csv_named
from excel_list_transform.handle_excel import read_excel_named
from extract_list.handle_output import handle_output
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import OutFileType
from extract_list.commontypes import Data, Value
from extract_list.handle_input import read_in_json, read_in_xml


DATA = [
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
    data: Data = list(indata['data'].values())
    return data


def read_json(filename: str, cfg: ExtractConfig) -> Data:
    """Read from JSON."""
    return read_in_json(filename=filename, encoding=cfg.outfile_encoding)


def read_csv(filename: str, cfg: ExtractConfig) -> Data:
    """Read from CSV."""
    return read_csv_named(filename=filename, dialect=cfg.out_csv_dialect,
                          encoding=cfg.outfile_encoding, max_column_read=20)


def read_excel(filename: str, cfg: ExtractConfig) -> Data:
    """Read from Excel."""
    return read_excel_named(filename=filename, max_column_read=20,
                            strip_col_names=False, strip_values=False,
                            excel_lib=cfg.outfile_excel_library)


@pytest.mark.parametrize('dat', DATA)
@pytest.mark.parametrize('enc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('typ, resfile, reader',
                         [(OutFileType.CSV, 'a.csv', read_csv),
                          (OutFileType.EXCEL, 'a.xlsx', read_excel),
                          (OutFileType.JSON, 'a.json', read_json),
                          (OutFileType.TXT, 'a.txt', read_txt),
                          (OutFileType.XML, 'a.xml', read_xml)])
def test_handle_output_ok1(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                           dat, enc, typ, resfile, reader):
    """Test OK cases 1 of handle_output."""
    cfg = ExtractConfig()
    cfg.outfile_encoding = enc
    cfg.outfile_type = typ
    cfg.column_order = dat[0].keys()
    cfg.out_xml_attributes = []
    with TemporaryDirectory() as dirname:
        fname = dirname + '/a'
        handle_output(data=dat, filename=fname, cfg=cfg)
        res_fname = dirname + '/' + resfile
        res_data = reader(filename=res_fname, cfg=cfg)
        assert res_data == dat
    check_capsys(capsys=capsys)
