#! /usr/local/bin/python3
"""Test command line parsing of extract_list (mocked functionality)."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

import pytest
from check_capsys import check_capsys
from extract_list.extract_cmd import extract_cmd


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_main(capsys, hflag):
    """Test help printout of main command."""
    cmd = [hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list [-h] {cfg-example,extract}',
        'Extract data from an input file in JSON or XML format',
        'Generate example configuration file',
        'Extract list of columns of data from JSON or XML'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_extract(capsys, hflag):
    """Test help printout of extract sub-command."""
    cmd = ['extract', hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list extract [-h] -c CFG -i INPUT -o OUTPUT',
        'Extract list of columns of data from JSON or XML input.',
        'See also help text for', 'main command without sub-commands.',
        '-c CFG, --cfg CFG     Configuation file name to use.',
        '-i INPUT, --input INPUT',
        '-o OUTPUT, --output OUTPUT'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_example(capsys, hflag):
    """Test help printout of cfg-example sub-command."""
    cmd = ['cfg-example', hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list cfg-example [-h] -k',
        'Generate example configuration file (example .cfg file).',
        '-k {sw_json_to_rrs,sw_xml_to_rrs',
        '-t {excel,csv,json,xml,txt},',
        '--typeofoutput {excel,csv,json,xml,txt}',
        '-o OUTPUT, --output OUTPUT'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('cflag', ['-c', '--cfg'])
@pytest.mark.parametrize('cfg', ['a.cfg', 'gfc.cfg'])
@pytest.mark.parametrize('iflag', ['-i', '--input'])
@pytest.mark.parametrize('ival', ['abc', '2.json'])
@pytest.mark.parametrize('oflag', ['-o', '--output'])
@pytest.mark.parametrize('oval', ['gij', 'xy.csv'])
def test_cmdline_ok1(capsys,  # pylint: disable=too-many-positional-arguments,too-many-arguments # noqa: E501
                     monkeypatch, cflag, cfg, iflag, ival, oflag, oval):
    """Test parsing of command line for extract."""
    def patch(in_file_name: str, cfg_file_name: str,
              out_file_name: str) -> int:
        """Monkeypatch of extract_func."""
        assert cfg_file_name == cfg
        assert in_file_name == ival
        assert out_file_name == oval
        patch.calls += 1
        return 0
    patch.calls = 0
    monkeypatch.setattr('extract_list.extract_cmd.extract_func', patch)
    cmd = ['extract', oflag, oval, iflag, ival, cflag, cfg]
    _ = extract_cmd(arguments=cmd)
    assert patch.calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('kflag', ['-k', '--kind'])
@pytest.mark.parametrize('kval', ['sw_json_to_rrs', 'sw_xml_to_rrs',
                                  'example_json', 'example_xml'])
@pytest.mark.parametrize('tflag', ['-t', '--typeofoutput'])
@pytest.mark.parametrize('tval', ['excel', 'csv', 'json', 'xml', 'txt'])
@pytest.mark.parametrize('oflag', ['-o', '--output'])
@pytest.mark.parametrize('oval', ['gij', 'xy.cfg'])
def test_cmdline_ok2(capsys,  # pylint: disable=too-many-positional-arguments,too-many-arguments # noqa: E501
                     monkeypatch, kflag, kval, tflag, tval, oflag, oval):
    """Test parsing of command line for cfg-example."""
    def patch(filename: str, cfgtype: str,
              out_file_type: str) -> int:
        """Monkeypatch of generate_example_cfg."""
        assert out_file_type == tval
        assert cfgtype == kval
        assert filename == oval
        patch.calls += 1
        return 0
    patch.calls = 0
    monkeypatch.setattr('extract_list.extract_cmd.generate_example_cfg',
                        patch)
    cmd = ['cfg-example', oflag, oval, kflag, kval, tflag, tval]
    _ = extract_cmd(arguments=cmd)
    assert patch.calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('line, vals',
                         [('extract -o abc -i ghi -c klm',
                           {'oval': 'abc', 'ival': 'ghi', 'cval': 'klm'}),
                          ('extract -i hej -o hi -c bye',
                           {'oval': 'hi', 'ival': 'hej', 'cval': 'bye'}),
                          ('extract -c donald -i duck -o mickey',
                           {'oval': 'mickey', 'ival': 'duck',
                            'cval': 'donald'}),
                          ('extract -c KK -o MM -i LL',
                           {'oval': 'MM', 'ival': 'LL', 'cval': 'KK'}),
                          ('python -m extract_list.py extract ' +
                           '-i abc.xml -o def.xlsx -c ghi.cfg',
                           {'cval': 'ghi.cfg', 'ival': 'abc.xml',
                            'oval': 'def.xlsx'})])
def test_cmdline_ok3(capsys, monkeypatch, line: str, vals):
    """Test parsing of command line for extract."""
    def patch(in_file_name: str, cfg_file_name: str,
              out_file_name: str) -> int:
        """Monkeypatch of extract_func."""
        assert cfg_file_name == vals['cval']
        assert in_file_name == vals['ival']
        assert out_file_name == vals['oval']
        patch.calls += 1
        return 0
    patch.calls = 0
    monkeypatch.setattr('extract_list.extract_cmd.extract_func', patch)
    cmd = line.split()
    _ = extract_cmd(arguments=cmd)
    assert patch.calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('line, vals',
                         [('cfg-example -k example_json -t txt -o GH.cfg',
                           {'kval': 'example_json', 'tval': 'txt',
                            'oval': 'GH.cfg'}),
                          ('python3 -m extract_list/__main.py ' +
                           'cfg-example -o abc.cfg -t csv -k example_xml',
                           {'kval': 'example_xml', 'tval': 'csv',
                            'oval': 'abc.cfg'})])
def test_cmdline_ok4(capsys, monkeypatch, line: str, vals):
    """Test parsing of command line for cfg-example."""
    def patch(filename: str, cfgtype: str,
              out_file_type: str) -> int:
        """Monkeypatch of generate_example_cfg."""
        assert out_file_type == vals['tval']
        assert cfgtype == vals['kval']
        assert filename == vals['oval']
        patch.calls += 1
        return 0
    patch.calls = 0
    monkeypatch.setattr('extract_list.extract_cmd.generate_example_cfg',
                        patch)
    cmd = line.split()
    _ = extract_cmd(arguments=cmd)
    assert patch.calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('line,errmsgs',
                         [('-o out.xlsx -c cfg.cfg -i in.json',
                           ['error: argument subparser_name: invalid choice',
                            'usage: extract_list [-h] {cfg-example,extract}',
                            "(choose from 'cfg-example', 'extract')"]),
                          ('extract -i in.jspon -o out.xlsx -c a.cfg -b',
                           ['extract_list: error: unrecognized ' +
                            'arguments: -b']),
                          ('extract -i in.jspon -o out.xlsx',
                           ['error: the following arguments are required: ' +
                            '-c/--cfg',
                            'usage: extract_list extract [-h] -c CFG ' +
                            '-i INPUT -o OUTPUT']),
                          ('extract -o out.xlsx -c c.cfg',
                           ['error: the following arguments are required: ' +
                            '-i/--input',
                            'usage: extract_list extract [-h] -c CFG ' +
                            '-i INPUT -o OUTPUT']),
                          ('cfg-example',
                           ['error: the following arguments are required: ' +
                            '-k/--kind, -t/--typeofoutput, -o/--output']),
                          ('cfg-example -k abc -t csv -o out.cfg',
                           ['usage: extract_list cfg-example [-h] -k',
                            '{sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml}',
                            '-t {excel,csv,json,xml,txt} -o OUTPUT',
                            "invalid choice: 'abc' (choose from " +
                            "'sw_json_to_rrs', 'sw_xml_to_rrs', " +
                            "'example_json', 'example_xml')"]),
                          ('cfg-example -t csv -o out.cfg',
                           ['usage: extract_list cfg-example [-h] -k',
                            '{sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml}',
                            '-t {excel,csv,json,xml,txt} -o OUTPUT',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: -k/--kind']),
                          ('cfg-example -k sw_json_to_rrs -o out.cfg',
                           ['usage: extract_list cfg-example [-h] -k',
                            '{sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml}',
                            '-t {excel,csv,json,xml,txt} -o OUTPUT',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: ' +
                            '-t/--typeofoutput']),
                          ('cfg-example -k sw_json_to_rrs -t abc -o out.cfg',
                           ['usage: extract_list cfg-example [-h] -k',
                            '{sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml}',
                            '-t {excel,csv,json,xml,txt} -o OUTPUT',
                            "extract_list cfg-example: error: argument " +
                            "-t/--typeofoutput: invalid choice: 'abc' " +
                            "(choose from 'excel', 'csv', 'json', 'xml', " +
                            "'txt')"]),
                          ('cfg-example -k sw_json_to_rrs -t csv',
                           ['usage: extract_list cfg-example [-h] -k',
                            '{sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml}',
                            '-t {excel,csv,json,xml,txt} -o OUTPUT',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: ' +
                            '-o/--output'])])
def test_cmdline_nok1(capsys, line, errmsgs):
    """Test not OK command lines 1."""
    with pytest.raises(SystemExit):
        _ = extract_cmd(arguments=line.split())
    check_capsys(capsys=capsys, in_err=errmsgs)
