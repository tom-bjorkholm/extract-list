#! /usr/local/bin/python3
"""Test printing list of dicts as JSON and as XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

# import sys
# from tempfile import TemporaryDirectory
from copy import deepcopy
import pytest
from extract_list.config_enums import InFileType, OutFileType
from extract_list.extract_config import ExtractConfig, \
    MainLineSpec, MLineDict, _mline_spec_from_dict, \
    LinkedLineSpec, LLineDict, _linked_line_from_json_array


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_1(capsys, lin, col):
    """Test MainLineSprec (case 1)."""
    spec = MainLineSpec()
    spec.line = deepcopy(lin)
    spec.columns = deepcopy(col)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mainlinespec_2(capsys, lin, col):
    """Test MainLineSprec (case 2)."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col)}
    spec = MainLineSpec(mld)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']}),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']})])
def test_mlinespecfromdict(capsys, lin, col):
    """Test _mline_spec_from_dict."""
    mld: MLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col)}
    spec = _mline_spec_from_dict(data=mld)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    assert lin == spec.line
    assert col == spec.columns
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_linklinespec_1(capsys, lin, col, lmc, lcol):
    """Test LinkedLineSprec (case 1)."""
    spec = LinkedLineSpec()
    spec.line = deepcopy(lin)
    spec.columns = deepcopy(col)
    spec.linked_main_column = deepcopy(lmc)
    spec.linked_column = deepcopy(lcol)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_linklinespec_2(capsys,  # pylint: disable=too-many-locals
                        lin, col, lmc, lcol):
    """Test LinkedLineSprec (case 2)."""
    lld: LLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'linked_main_column': deepcopy(lmc),
                      'linked_column': deepcopy(lcol)}
    spec = LinkedLineSpec(data=lld)
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    assert lin == spec.line
    assert col == spec.columns
    assert lmc == spec.linked_main_column
    assert lcol == spec.linked_column
    assert '' == out
    assert '' == err


@pytest.mark.parametrize('lin, col, lmc, lcol',
                         [(['abc', 'def'], {'gh': ['ij', 'kl']},
                           ['rt', 'ty'], ['yu', 'ui']),
                          (['xf', 'as'], {'fds': ['a1', 'a2'],
                                          'col2': ['sdf', 'b1']},
                           ['a'], ['b', 'c'])])
def test_llinefromjson(capsys,  # pylint: disable=too-many-locals
                       lin, col, lmc, lcol):
    """Test _linked_line_from_json_array."""
    lld: LLineDict = {'line': deepcopy(lin),
                      'columns': deepcopy(col),
                      'linked_main_column': deepcopy(lmc),
                      'linked_column': deepcopy(lcol)}
    speclist = _linked_line_from_json_array(data=[lld, lld])
    assert len(speclist) == 2
    assert speclist[0].line == speclist[1].line
    assert speclist[0].linked_column == speclist[1].linked_column
    assert speclist[0].linked_main_column == speclist[1].linked_main_column
    spec = speclist[0]
    txt = str(spec)
    out, err = capsys.readouterr()
    for lpart in lin:
        assert lpart in txt
    for key, val in col.items():
        assert key in txt
        for elem in val:
            assert elem in txt
    for lmpart in lmc:
        assert lmpart in txt
    for lcp in lcol:
        assert lcp in txt
    assert lin == spec.line
    assert col == spec.columns
    assert lmc == spec.linked_main_column
    assert lcol == spec.linked_column
    assert '' == out
    assert '' == err


# TODO test check methods

def test_extract_config_nochange(capsys):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    assert cfg.infile_type == cf2.infile_type
    assert cfg.infile_encoding == cf2.infile_encoding
    assert cfg.in_xml_strip_at == cf2.in_xml_strip_at
    assert cfg.include_key == cf2.include_key
    assert cfg.column_name_for_key == cf2.column_name_for_key
    assert cfg.missing_input_for_column == cf2.missing_input_for_column
    assert cfg.main_line.line == cf2.main_line.line
    assert cfg.main_line.columns == cf2.main_line.columns
    assert len(cfg.linked_lines) == len(cf2.linked_lines)
    for elem1, elem2 in zip(cfg.linked_lines, cf2.linked_lines):
        assert elem1.line == elem2.line
    assert cfg.outfile_type == cf2.outfile_type
    assert cfg.outfile_encoding == cf2.outfile_encoding
    assert cfg.outfile_excel_library == cf2.outfile_excel_library
    assert cfg.column_order == cf2.column_order
    assert cfg.out_xml_attributes == cf2.out_xml_attributes
    assert cfg.out_csv_dialect == cf2.out_csv_dialect
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('inenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('infiletype', [InFileType.JSON, InFileType.XML])
@pytest.mark.parametrize('outenc', ['utf-8', 'iso8859-1'])
@pytest.mark.parametrize('outfiletype',
                         [OutFileType.JSON, OutFileType.XML, OutFileType.CSV,
                          OutFileType.EXCEL, OutFileType.TXT])
def test_extract_config_var1(capsys, inenc, infiletype, outenc, outfiletype):
    """Test default configured ExtractConfig."""
    cfg = ExtractConfig()
    cfg.infile_encoding = deepcopy(inenc)
    cfg.outfile_encoding = deepcopy(outenc)
    cfg.infile_type = deepcopy(infiletype)
    cfg.outfile_type = deepcopy(outfiletype)
    txt = cfg.as_json_string()
    cf2 = ExtractConfig(from_json_data_text=txt)
    assert cf2.infile_type == infiletype
    assert cfg.infile_type == cf2.infile_type
    assert cf2.infile_encoding == inenc
    assert cfg.infile_encoding == cf2.infile_encoding
    assert cfg.in_xml_strip_at == cf2.in_xml_strip_at
    assert cfg.include_key == cf2.include_key
    assert cfg.column_name_for_key == cf2.column_name_for_key
    assert cfg.missing_input_for_column == cf2.missing_input_for_column
    assert cfg.main_line.line == cf2.main_line.line
    assert cfg.main_line.columns == cf2.main_line.columns
    assert len(cfg.linked_lines) == len(cf2.linked_lines)
    for elem1, elem2 in zip(cfg.linked_lines, cf2.linked_lines):
        assert elem1.line == elem2.line
    assert cf2.outfile_type == outfiletype
    assert cfg.outfile_type == cf2.outfile_type
    assert cf2.outfile_encoding == outenc
    assert cfg.outfile_encoding == cf2.outfile_encoding
    assert cfg.outfile_excel_library == cf2.outfile_excel_library
    assert cfg.column_order == cf2.column_order
    assert cfg.out_xml_attributes == cf2.out_xml_attributes
    assert cfg.out_csv_dialect == cf2.out_csv_dialect
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


# TODO test variations of valid configuraitons
# TODO test messages for variations of invalid configurations
