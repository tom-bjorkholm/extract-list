#! /usr/local/bin/python3
"""Test command line parsing of extract_list (mocked functionality)."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from datetime import date
from importlib.metadata import version as metadata_version
import pytest
from extract_list.extract_cmd import extract_cmd
from .check_capsys import check_capsys


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_main(capsys: pytest.CaptureFixture[str], hflag: str) -> None:
    """Test help printout of main command."""
    cmd = [hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list [-h] {cfg-example,extract,version,migrate-cfg}',
        'Extract data from an input file in JSON or XML format',
        'Generate example configuration file',
        'Extract list of columns of data from JSON or XML',
        'Only print versions of extract_list'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_extract(capsys: pytest.CaptureFixture[str], hflag: str) -> None:
    """Test help printout of extract sub-command."""
    cmd = ['extract', hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list extract [-h] -c CFG -i INPUT -o OUTPUT',
        'Extract list of columns of data from JSON or XML input.',
        'See also help text for', 'main command without sub-commands.',
        '-c, --cfg CFG', 'Configuation file name to use.',
        '-i, --input INPUT',
        '-o, --output OUTPUT'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_example(capsys: pytest.CaptureFixture[str], hflag: str) -> None:
    """Test help printout of cfg-example sub-command."""
    cmd = ['cfg-example', hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list cfg-example [-h]',
        'Generate example configuration file (example .cfg file).',
        '-k {sw_json_to_rrs,sw_xml_to_rrs',
        '-t {CSV,csv,Csv,Excel,',
        '--typeofoutput {CSV,csv,Csv,Excel,',
        '-o, --output OUTPUT'
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('hflag', ['-h', '--help'])
def test_help_version(capsys: pytest.CaptureFixture[str], hflag: str) -> None:
    """Test help printout of cfg-example sub-command."""
    cmd = ['version', hflag]
    with pytest.raises(SystemExit):
        _ = extract_cmd(cmd)
    msgs = [
        'usage: extract_list version [-h]',
        'Only print versions of extract_list',
    ]
    check_capsys(capsys=capsys, in_out=msgs)


@pytest.mark.parametrize('cflag', ['-c', '--cfg'])
@pytest.mark.parametrize('cfg', ['a.cfg', 'gfc.cfg'])
@pytest.mark.parametrize('iflag', ['-i', '--input'])
@pytest.mark.parametrize('ival', ['abc', '2.json'])
@pytest.mark.parametrize('oflag', ['-o', '--output'])
@pytest.mark.parametrize('oval', ['gij', 'xy.csv'])
def test_cmdline_ok1(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-positional-arguments,too-many-arguments # noqa: E501
                     monkeypatch: pytest.MonkeyPatch, cflag: str, cfg: str,
                     iflag: str, ival: str, oflag: str, oval: str) -> None:
    """Test parsing of command line for extract."""
    calls = 0

    def patch(in_file_name: str, cfg_file_name: str,
              out_file_name: str) -> int:
        """Monkeypatch of extract_func."""
        nonlocal calls
        assert cfg_file_name == cfg
        assert in_file_name == ival
        assert out_file_name == oval
        calls += 1
        return 0
    monkeypatch.setattr('extract_list.extract_cmd.extract_func', patch)
    cmd = ['extract', oflag, oval, iflag, ival, cflag, cfg]
    _ = extract_cmd(arguments=cmd)
    assert calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('kflag', ['-k', '--kind'])
@pytest.mark.parametrize('kval', ['sw_json_to_rrs', 'sw_xml_to_rrs',
                                  'example_json', 'example_xml'])
@pytest.mark.parametrize('tflag', ['-t', '--typeofoutput'])
@pytest.mark.parametrize('tval', ['excel', 'csv', 'json', 'xml', 'txt'])
@pytest.mark.parametrize('oflag', ['-o', '--output'])
@pytest.mark.parametrize('oval', ['gij', 'xy.cfg'])
def test_cmdline_ok2(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-positional-arguments,too-many-arguments # noqa: E501
                     monkeypatch: pytest.MonkeyPatch, kflag: str, kval: str,
                     tflag: str, tval: str, oflag: str, oval: str) -> None:
    """Test parsing of command line for cfg-example."""
    calls = 0

    def patch(filename: str, cfgtype: str, out_file_type: str) -> int:
        """Monkeypatch of generate_example_cfg."""
        nonlocal calls
        assert out_file_type == tval
        assert cfgtype == kval
        assert filename == oval
        calls += 1
        return 0
    monkeypatch.setattr('extract_list.extract_cmd.generate_example_cfg', patch)
    cmd = ['cfg-example', oflag, oval, kflag, kval, tflag, tval]
    _ = extract_cmd(arguments=cmd)
    assert calls == 1
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
def test_cmdline_ok3(capsys: pytest.CaptureFixture[str],
                     monkeypatch: pytest.MonkeyPatch, line: str,
                     vals: dict[str, str]) -> None:
    """Test parsing of command line for extract."""
    calls = 0

    def patch(in_file_name: str, cfg_file_name: str,
              out_file_name: str) -> int:
        """Monkeypatch of extract_func."""
        nonlocal calls
        assert cfg_file_name == vals['cval']
        assert in_file_name == vals['ival']
        assert out_file_name == vals['oval']
        calls += 1
        return 0
    monkeypatch.setattr('extract_list.extract_cmd.extract_func', patch)
    cmd = line.split()
    _ = extract_cmd(arguments=cmd)
    assert calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('line, vals',
                         [('cfg-example -k example_json -t txt -o GH.cfg',
                           {'kval': 'example_json', 'tval': 'txt',
                            'oval': 'GH.cfg'}),
                          ('python3 -m extract_list/__main.py ' +
                           'cfg-example -o abc.cfg -t csv -k example_xml',
                           {'kval': 'example_xml', 'tval': 'csv',
                            'oval': 'abc.cfg'})])
def test_cmdline_ok4(capsys: pytest.CaptureFixture[str],
                     monkeypatch: pytest.MonkeyPatch, line: str,
                     vals: dict[str, str]) -> None:
    """Test parsing of command line for cfg-example."""
    calls = 0

    def patch(filename: str, cfgtype: str, out_file_type: str) -> int:
        """Monkeypatch of generate_example_cfg."""
        nonlocal calls
        assert out_file_type == vals['tval']
        assert cfgtype == vals['kval']
        assert filename == vals['oval']
        calls += 1
        return 0
    monkeypatch.setattr('extract_list.extract_cmd.generate_example_cfg', patch)
    cmd = line.split()
    _ = extract_cmd(arguments=cmd)
    assert calls == 1
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('line,errmsgs',
                         [('-o out.xlsx -c cfg.cfg -i in.json',
                           ['error: argument subparser_name: invalid choice',
                            'usage: extract_list [-h] {cfg-example,extract,'
                            'version,migrate-cfg}',
                            "invalid choice: 'out.xlsx' (choose from"]),
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
                           ['usage: extract_list cfg-example [-h]',
                            '-k {sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml,' +
                            'example2_json,example2_xml}',
                            '-t {CSV,',
                            'extract_list cfg-example: error: argument ' +
                            "-k/--kind: invalid choice: 'abc'",
                            '(choose from']),
                          ('cfg-example -t csv -o out.cfg',
                           ['usage: extract_list cfg-example [-h]',
                            '-k {sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml,' +
                            'example2_json,example2_xml}',
                            '-t {CSV,',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: -k/--kind']),
                          ('cfg-example -k sw_json_to_rrs -o out.cfg',
                           ['usage: extract_list cfg-example [-h]',
                            '-k {sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml,' +
                            'example2_json,example2_xml}',
                            '-t {CSV,',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: ' +
                            '-t/--typeofoutput']),
                          ('cfg-example -k sw_json_to_rrs -t abc -o out.cfg',
                           ['usage: extract_list cfg-example [-h]',
                            '-k {sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml,' +
                            'example2_json,example2_xml}',
                            '-t {CSV,',
                            "extract_list cfg-example: error: argument " +
                            "-t/--typeofoutput: invalid choice: 'abc'",
                            '(choose from']),
                          ('cfg-example -k sw_json_to_rrs -t csv',
                           ['usage: extract_list cfg-example [-h]',
                            '-k {sw_json_to_rrs,sw_xml_to_rrs,' +
                            'example_json,example_xml,' +
                            'example2_json,example2_xml}',
                            '-t {CSV,csv,Csv,Excel,',
                            'extract_list cfg-example: error: the ' +
                            'following arguments are required: ' +
                            '-o/--output'])])
def test_cmdline_nok1(capsys: pytest.CaptureFixture[str], line: str,
                      errmsgs: list[str]) -> None:
    """Test not OK command lines 1."""
    with pytest.raises(SystemExit):
        _ = extract_cmd(arguments=line.split())
    check_capsys(capsys=capsys, in_err=errmsgs)


def test_version_cmd1(capsys: pytest.CaptureFixture[str],
                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Test command to print version information."""
    monkeypatch.setattr('extract_list.xl_version.XlVersion.' +
                        '_print_info_on_new_pkgs',
                        lambda self, versions=None: None)
    extract_cmd(['version'])
    out, err = capsys.readouterr()
    assert '' == err
    assert 'Python ' in out
    assert 'extract_list ' in out
    assert str(metadata_version("extract_list")) in out


@pytest.mark.parametrize('ver, dat, errprint',
                         [((3, 11, 1, 0, 0),
                           date(year=2026, month=12, day=25), True),
                          ((3, 11, 1, 0, 0),
                           date(year=2024, month=12, day=25), False),
                          ((3, 10, 11, 75, 0),
                           date(year=2027, month=12, day=25), True)])
def test_version_check_if_u(capsys: pytest.CaptureFixture[str],
                            monkeypatch: pytest.MonkeyPatch,
                            ver: tuple[int, int, int, int, int], dat: date,
                            errprint: bool) -> None:
    """Test version check if unsupported python widh old Python."""
    mod = 'versionreporter.versionreporter.'
    monkeypatch.setattr(mod + 'sys.version_info', ver)

    def mock_day(_: object) -> date:
        """Mock Version._today."""
        return dat

    monkeypatch.setattr(mod + 'VersionReporter._today', mock_day)
    with pytest.raises(SystemExit):
        extract_cmd(['--help'])
    out, err = capsys.readouterr()
    assert '' == err
    if errprint:
        assert 'You are running an old version of Python:' in out
        assert 'This application no longer releases bug fixes ' in out
        assert 'for this old Python version.' in out
        assert 'Upgrade Python to a new version.' in out
        assert '(Download Python from https://www.python.org/downloads' in out
        assert 'After installing new Python, upgrade application with' in out
        assert ' install --upgrade ' in out
    else:
        assert 'You are running an old version of Python:' not in out
        assert 'This application no longer releases bug fixes ' not in out
        assert 'for this old Python version.' not in out
        assert 'Upgrade Python to a new version.' not in out
        assert '(Download Python from https://www.python.or' not in out
        assert 'After installing new Python, upgrade application ' not in out
        assert ' install --upgrade ' not in out
