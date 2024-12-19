#! /usr/local/bin/python3
"""Test extracting of data with files for extract list."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from copy import deepcopy
from tempfile import TemporaryDirectory
import pytest
from example_data import ExampleData
from test_handle_output import read_csv, read_excel, read_json
from check_capsys import check_capsys
from extract_list.extract_func import extract_func
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import InFileType, OutFileType


def incr_calls(num_calls: dict[str, dict[int, int]], ind_one: str,
               ind_two: int):
    """Increment or create call record if indexes."""
    if ind_one not in num_calls:
        num_calls[ind_one] = {ind_two: 1}
        return
    if ind_two not in num_calls[ind_one]:
        num_calls[ind_one][ind_two] = 1
        return
    num_calls[ind_one][ind_two] += 1


@pytest.mark.parametrize('inpar',
                         [(InFileType.JSON, 'a.json',
                           ExampleData.write_json_to_file),
                          (InFileType.XML, 'b.xml',
                           ExampleData.write_xml_to_file)])
@pytest.mark.parametrize('inenc', ['utf-8', 'iso-8859-1'])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso-8859-1'])
@pytest.mark.parametrize('cfgname', ['a2.cfg', 'bcd.cfg'])
@pytest.mark.parametrize('outpar',
                         [(OutFileType.CSV, 'c.csv', read_csv),
                          (OutFileType.EXCEL, 'd.xlsx', read_excel),
                          (OutFileType.JSON, 'x.json', read_json)])
def test_extract_func_ok1(capsys,  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals # noqa: E501
                          inpar, inenc, outenc, cfgname, outpar):
    """Test OK use cases 1 of extract_func."""
    with TemporaryDirectory() as dirname:
        cfg = deepcopy(ExtractConfig())
        cfg.infile_type = inpar[0]
        cfg.in_xml_strip_at = True
        cfg.infile_encoding = inenc
        cfg.outfile_type = outpar[0]
        cfg.outfile_encoding = outenc
        cfg_fullname = dirname + '/' + cfgname
        infilename = dirname + '/' + inpar[1]
        outfilename = dirname + '/' + outpar[1]
        if inpar[0] == InFileType.XML:
            cfg.main_line.line.insert(0, 'data')
            cfg.linked_lines[0].line.insert(0, 'data')
        cfg.write(cfg_fullname)
        exdata = ExampleData()
        inpar[2](exdata, infilename, inenc)
        ret = extract_func(in_file_name=infilename,
                           cfg_file_name=cfg_fullname,
                           out_file_name=outfilename)
        assert 0 == ret
        check_capsys(capsys=capsys)
        data = outpar[2](filename=outfilename, cfg=cfg)
        assert len(data) == 5
        num_calls = {}
        for row in data:
            assert len(row) == 6
            assert 'What' in row
            if row['What'] == 'carrot':
                incr_calls(num_calls, 'carrot', 345)
                assert int(row['How many']) == 2
                assert row['Customer name'] == 'Donald Duck'
                assert row['Street'] == 'Some Road'
                assert int(row['Street number']) == 666
                assert str(row['key col']) in ['345', 'i_345']
            if row['What'] == 'orange' and 'Donald' in row['Customer name']:
                incr_calls(num_calls, 'orange', 345)
                assert int(row['How many']) == 20
                assert row['Customer name'] == 'Donald Duck'
                assert row['Street'] == 'Some Road'
                assert int(row['Street number']) == 666
                assert str(row['key col']) in ['345', 'i_345']
            if row['What'] == 'orange' and 'Mouse' in row['Customer name']:
                incr_calls(num_calls, 'orange', 234)
                assert int(row['How many']) == 6
                assert row['Customer name'] == 'Mickey Mouse'
                assert row['Street'] == 'Another Street'
                assert int(row['Street number']) == 7
                assert str(row['key col']) in ['234', 'i_234']
        assert num_calls['carrot'][345] == 1
        assert num_calls['orange'][345] == 1
        assert num_calls['orange'][234] == 1
