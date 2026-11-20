#! /usr/local/bin/python3
"""Test reading a dict at line as one record (dict_at_line_is_record).

An XML element that is repeated becomes a list, but the same element
occurring only once becomes a dict. These tests check that a line
specification with dict_at_line_is_record true reads such a dict as one
record, and that false keeps reading a dict as records keyed by name.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from collections.abc import Callable
from pathlib import Path
import sys
import pytest
import xmltodict
from config_as_json import JsonPath, JsonType
from extract_list.commontypes import CfgTypes, Data, Value
from extract_list.config_enums import MissingInputForColumn
from extract_list.extract_config import ExtractConfig
from extract_list.extract_config_params import MainLineSpec
from extract_list.extract_data import get_lines
from extract_list.extract_func import extract_func
from extract_list.generate_cfg import generate_cfg_example, \
    generate_cfg_example2, generate_cfg_sw_to_rrs
from extract_list.xl_migrate_cfg_warn_hook import XlMigrateCfgWarnHook
from .bogus_cfg import cfg_text_without
from .check_capsys import check_capsys
from .check_result import check_result, ex_res, ex2_res
from .example_data import ExampleData
from .test_generate_cfg import sw_res_data
from .test_handle_output import read_csv, read_json

REC_A: JsonType = {'name': 'A', 'items': [{'n': 1}, {'n': 2}]}
REC_B: JsonType = {'name': 'B', 'items': {'n': 3}}
KEYED: JsonType = {'a': REC_A, 'b': REC_B}


@pytest.mark.parametrize('at_line, is_record, expand_at, expected', [
    (KEYED, False, [], [('a', REC_A), ('b', REC_B)]),
    (KEYED, True, [], [(0, KEYED)]),
    (REC_B, True, [], [(0, REC_B)]),
    (REC_A, True, [['items']], [(0, {'name': 'A', 'items': {'n': 1}}),
                                (0, {'name': 'A', 'items': {'n': 2}})]),
    ([REC_A, REC_B], False, [], [(0, REC_A), (1, REC_B)]),
    ([REC_A, REC_B], True, [], [(0, REC_A), (1, REC_B)]),
    ('x', True, [], [(0, 'x')])])
def test_get_lines_dict(capsys: pytest.CaptureFixture[str], at_line: JsonType,
                        is_record: bool, expand_at: list[list[str]],
                        expected: list[tuple[Value, JsonType]]) -> None:
    """Test how get_lines reads what it finds at line.

    Only a dict is affected by dict_at_line_is_record. A dict that is one
    record gets key 0, like the only element of a list.
    """
    spec = MainLineSpec(data={'line': ['top', 'recs'], 'columns': {},
                              'expand_at': expand_at,
                              'dict_at_line_is_record': is_record})
    indata: JsonType = {'top': {'recs': at_line}}
    result = list(get_lines(indata=indata, missing=MissingInputForColumn.ERROR,
                            spec=spec))
    assert result == expected
    check_capsys(capsys=capsys)


def one_customer() -> ExampleData:
    """Return example data with one customer, Donald Duck, only.

    Only his orders and only the delivery method for his street are kept,
    so that customers and delivery_method each occur once.
    """
    example = ExampleData()
    data = example.data
    assert isinstance(data['customers'], list)
    assert isinstance(data['orders'], dict)
    assert isinstance(data['delivery_method'], list)
    data['customers'] = data['customers'][:1]
    data['orders'] = {key: order for key, order in data['orders'].items()
                      if key != '234'}
    data['delivery_method'] = data['delivery_method'][1:]
    return example


def donald_rows(rows: Data) -> Data:
    """Return the rows of the expected result that are Donald Duck's."""
    return [row for row in rows if row['Customer name'] == 'Donald Duck']


GenCfg = Callable[[str, CfgTypes, str], int]
WriteData = Callable[[ExampleData, str], None]


@pytest.mark.parametrize('cfgtype, gen_cfg, write, expected', [
    (CfgTypes.EXAMPLE_XML, generate_cfg_example,
     ExampleData.write_xml_to_file, donald_rows(ex_res)),
    (CfgTypes.EXAMPLE2_XML, generate_cfg_example2,
     ExampleData.write_xml_to_file, donald_rows(ex2_res)),
    (CfgTypes.EXAMPLE_JSON, generate_cfg_example,
     ExampleData.write_json_to_file, donald_rows(ex_res)),
    (CfgTypes.EXAMPLE2_JSON, generate_cfg_example2,
     ExampleData.write_json_to_file, donald_rows(ex2_res))])
def test_one_customer(capsys: pytest.CaptureFixture[str], tmp_path: Path,  # pylint: disable=too-many-arguments,too-many-positional-arguments # noqa: E501
                      cfgtype: CfgTypes, gen_cfg: GenCfg, write: WriteData,
                      expected: Data) -> None:
    """Test the example configurations with input of only one customer."""
    in_fname = str(tmp_path / 'in')
    cfg_fname = str(tmp_path / 'c.cfg')
    out_fname = str(tmp_path / 'out.json')
    write(one_customer(), in_fname)
    assert gen_cfg(cfg_fname, cfgtype, 'JSON') == 0
    assert extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                        out_file_name=out_fname) == 0
    cfg = ExtractConfig(from_json_filename=cfg_fname)
    check_result(result_data=read_json(out_fname, cfg), other_result=expected)
    check_capsys(capsys=capsys)


def test_one_customer_keyed(capsys: pytest.CaptureFixture[str],
                            tmp_path: Path) -> None:
    """Test that one XML customer read as keyed records is an error.

    This is the case dict_at_line_is_record is for: with it false, the
    single customer is read as records named name, address and so on.
    """
    in_fname = str(tmp_path / 'in.xml')
    cfg_fname = str(tmp_path / 'c.cfg')
    one_customer().write_xml_to_file(in_fname)
    generate_cfg_example2(cfg_fname, CfgTypes.EXAMPLE2_XML, 'JSON')
    cfg = ExtractConfig(from_json_filename=cfg_fname)
    cfg.main_line.dict_at_line_is_record = False
    cfg.write(to_json_filename=cfg_fname)
    with pytest.raises(SystemExit):
        extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                     out_file_name=str(tmp_path / 'out.json'))
    check_capsys(capsys=capsys, in_err=[
        'Input data does not match configuration', 'not dict'])


def write_one_competitor(filename: str, sail_number: str) -> None:
    """Write the Sailwave XML example with only one competitor kept."""
    sw_xml = Path(__file__).parent / 'SW.xml'
    data = xmltodict.parse(sw_xml.read_text(encoding='cp1252'))
    competitors = data['sailwave-data']['competitors']
    kept = [comp for comp in competitors['competitor']
            if comp['compsailno'] == sail_number]
    assert len(kept) == 1
    competitors['competitor'] = kept[0]
    with open(file=filename, mode='w', encoding='cp1252') as file:
        xmltodict.unparse(data, output=file, encoding='ISO-8859-1')


@pytest.mark.parametrize('sail_number', ['123', '456'])
def test_sw_one_competitor(capsys: pytest.CaptureFixture[str], tmp_path: Path,
                           sail_number: str) -> None:
    """Test the Sailwave XML configuration for a regatta of one boat."""
    in_fname = str(tmp_path / 'in.xml')
    cfg_fname = str(tmp_path / 'c.cfg')
    out_fname = str(tmp_path / 'out.csv')
    write_one_competitor(in_fname, sail_number)
    assert generate_cfg_sw_to_rrs(cfg_fname, CfgTypes.SW_XML_TO_RRS,
                                  'CSV') == 0
    assert extract_func(in_file_name=in_fname, cfg_file_name=cfg_fname,
                        out_file_name=out_fname) == 0
    cfg = ExtractConfig(from_json_filename=cfg_fname)
    expected = [row for row in sw_res_data
                if row['Sail Number'] == sail_number]
    check_result(result_data=read_csv(out_fname, cfg), other_result=expected)
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('path', [
    ('main_line', 'dict_at_line_is_record'),
    ('linked_lines', 0, 'dict_at_line_is_record')])
def test_old_cfg_is_keyed(capsys: pytest.CaptureFixture[str],
                          path: JsonPath) -> None:
    """Test that a file without dict_at_line_is_record reads it as false.

    That is how earlier versions read a dict at line, but the file is in
    an older format, so the user is asked to migrate it.
    """
    cfg = ExtractConfig(from_json_data_text=cfg_text_without(path),
                        auto_ch_hook=XlMigrateCfgWarnHook(),
                        stderr_file=sys.stderr)
    assert not cfg.main_line.dict_at_line_is_record
    assert not cfg.linked_lines[0].dict_at_line_is_record
    check_capsys(capsys=capsys, in_err=['Backward compatibility',
                                        'migrate-cfg'])


@pytest.mark.parametrize('cfgtype, gen_cfg, expected', [
    (CfgTypes.EXAMPLE_JSON, generate_cfg_example, [False, False]),
    (CfgTypes.EXAMPLE_XML, generate_cfg_example, [False, True]),
    (CfgTypes.EXAMPLE2_JSON, generate_cfg_example2, [False, False, False]),
    (CfgTypes.EXAMPLE2_XML, generate_cfg_example2, [True, False, True]),
    (CfgTypes.SW_JSON_TO_RRS, generate_cfg_sw_to_rrs, [False]),
    (CfgTypes.SW_XML_TO_RRS, generate_cfg_sw_to_rrs, [True])])
def test_generated_cfg(capsys: pytest.CaptureFixture[str], tmp_path: Path,
                       cfgtype: CfgTypes, gen_cfg: GenCfg,
                       expected: list[bool]) -> None:
    """Test dict_at_line_is_record of the main and linked lines generated.

    It is true only for XML input where line ends at a repeated element,
    and false where line ends at an element holding keyed records.
    """
    cfg_fname = str(tmp_path / 'c.cfg')
    assert gen_cfg(cfg_fname, cfgtype, 'CSV') == 0
    cfg = ExtractConfig(from_json_filename=cfg_fname)
    specs = [cfg.main_line, *cfg.linked_lines]
    assert [spec.dict_at_line_is_record for spec in specs] == expected
    check_capsys(capsys=capsys)
