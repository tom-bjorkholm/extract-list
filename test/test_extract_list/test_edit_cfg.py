#! /usr/local/bin/python3
"""Test the editcfg sub-command and the descriptions it shows.

The editing sessions use the "dump" user interface of edit-cfg-json, which
prints what the editor would show and needs neither display nor terminal.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from pathlib import Path
from typing import Optional
import sys
import pytest
from config_as_json import Config, ConfigPath
from edit_cfg_json import NoEditorError, Settings, UiBackend, chosen_ui, \
    editor_model
from extract_list.cfg_descriptions import EVERY, extract_descriptions
from extract_list import edit_cfg
from extract_list.extract_cmd import extract_cmd
from extract_list.extract_config import ExtractConfig
from .bogus_cfg import write_bogus_cfg
from .check_capsys import check_capsys


@pytest.fixture(autouse=True)
def no_user_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the editor settings of whoever runs the tests out of them."""
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setenv('USERPROFILE', str(tmp_path))
    monkeypatch.delenv('CFG_EDIT_CFG_JSON', raising=False)


def _populated_config() -> ExtractConfig:
    """Return a configuration where every list holds an element."""
    cfg = ExtractConfig()
    cfg.order_rows_by = ['What']
    cfg.linked_lines[0].expand_at = [['address']]
    return cfg


def _selects(selector: ConfigPath, path: ConfigPath) -> bool:
    """Return whether a description selector addresses the path."""
    return len(selector) == len(path) and \
        all(step in (EVERY, part) for step, part in zip(selector, path))


def test_every_row_described() -> None:
    """Test that the editor has a description for every member."""
    model = editor_model(_populated_config(),
                         descriptions=extract_descriptions())
    assert [row.path for row in model.rows if not row.description] == []


def test_no_unused_selector() -> None:
    """Test that every own description addresses a member (no typos)."""
    paths = [row.path for row in editor_model(_populated_config()).rows]
    own = [sel for sel in extract_descriptions() if sel[0] != 'output']
    unused = [sel for sel in own
              if not any(_selects(sel, path) for path in paths)]
    assert unused == []


@pytest.mark.parametrize('member', ['format_name', 'implementation',
                                    'character_encoding'])
def test_output_internal_told(member: str) -> None:
    """Test that the output texts mention extract-list's own formats."""
    assert 'Plaintxt' in extract_descriptions()[('output', member)]


@pytest.mark.parametrize('subcmd', ['editcfg', 'edit-cfg'])
@pytest.mark.parametrize('name', ['my.cfg', 'my'])
def test_editcfg_dump(capsys: pytest.CaptureFixture[str], tmp_path: Path,
                      subcmd: str, name: str) -> None:
    """Test that the editor opens with descriptions, also without .cfg."""
    ExtractConfig().write(tmp_path / 'my.cfg')
    ret = extract_cmd([subcmd, '-i', str(tmp_path / name), '--ui', 'dump'])
    assert ret == 0
    msgs = ['main_line', 'The records that become the lines of the output',
            'Nothing was saved.']
    check_capsys(capsys=capsys, in_out=msgs)


def test_editcfg_missing(capsys: pytest.CaptureFixture[str],
                         tmp_path: Path) -> None:
    """Test that a missing input file is explained, with a hint."""
    ret = extract_cmd(['editcfg', '-i', str(tmp_path / 'none'), '--ui',
                       'dump'])
    assert ret == 1
    msgs = ['none.cfg with configuration does not exist', 'cfg-example']
    check_capsys(capsys=capsys, in_err=msgs)


def test_editcfg_invalid(capsys: pytest.CaptureFixture[str],
                         tmp_path: Path) -> None:
    """Test that a file with invalid values is refused with the reason."""
    write_bogus_cfg(tmp_path / 'bad.cfg')
    ret = extract_cmd(['editcfg', '-i', str(tmp_path / 'bad.cfg'), '--ui',
                       'dump'])
    assert ret == 1
    msgs = ['cannot be opened', 'column_order includes column "Bogus"']
    check_capsys(capsys=capsys, in_err=msgs)


def test_editcfg_bad_ui(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that only the user interfaces that can run here are accepted."""
    with pytest.raises(SystemExit):
        extract_cmd(['editcfg', '-i', 'x.cfg', '--ui', 'nonexistent'])
    msgs = ["argument --ui: invalid choice: 'nonexistent'", "'dump'"]
    check_capsys(capsys=capsys, in_err=msgs)


@pytest.mark.parametrize('out_file', [None, 'other.cfg'])
@pytest.mark.parametrize('saved', [True, False])
def test_edit_cfg_func_args(capsys: pytest.CaptureFixture[str],
                            monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                            out_file: Optional[str], saved: bool) -> None:
    """Test what the editor is given, and the outcome of a session."""
    in_file = tmp_path / 'in.cfg'
    ExtractConfig().write(in_file)
    seen: dict[str, object] = {}

    def fake_edit(config: Config, **kwargs: object) -> Optional[Config]:
        """Record the keywords, and save or not."""
        seen.update(kwargs)
        return config if saved else None
    monkeypatch.setattr(edit_cfg, 'edit_in_ui', fake_edit)
    ret = edit_cfg.edit_cfg_func(in_file=str(in_file), out_file=out_file,
                                 ui_name='dump', stderr_file=sys.stderr)
    assert ret == 0
    assert (seen['in_file'], seen['out_file'], seen['ui_name']) == \
        (str(in_file), out_file, 'dump')
    assert seen['descriptions'] == extract_descriptions()
    settings = seen['settings']
    assert isinstance(settings, Settings)
    assert settings.file_extension == '.cfg'
    check_capsys(capsys=capsys, in_out=None if saved else 'Nothing was saved.')


def test_edit_cfg_no_editor(capsys: pytest.CaptureFixture[str],
                            monkeypatch: pytest.MonkeyPatch,
                            tmp_path: Path) -> None:
    """Test that a machine with no usable editor gets a message."""
    in_file = tmp_path / 'in.cfg'
    ExtractConfig().write(in_file)

    def no_editor(**_: object) -> UiBackend:
        """Refuse as edit-cfg-json does where no editor can run."""
        raise NoEditorError('There is no editor here.')
    monkeypatch.setattr(edit_cfg, 'chosen_ui', no_editor)
    ret = edit_cfg.edit_cfg_func(in_file=str(in_file), out_file=None,
                                 ui_name=None, stderr_file=sys.stderr)
    assert ret == 1
    check_capsys(capsys=capsys, in_err='There is no editor here.')


@pytest.mark.parametrize('name, named_by_env',
                         [('named.cfg', True),
                          ('.edit-cfg-json-tk.cfg', False),
                          ('.edit-cfg-json.cfg', False)])
def test_session_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                          name: str, named_by_env: bool) -> None:
    """Test that the user's settings are used, but saving as .cfg."""
    settings_file = tmp_path / name
    settings_file.write_text('{"backup_count": 3, "file_extension": ".json"}',
                             encoding='utf-8')
    if named_by_env:
        monkeypatch.setenv('CFG_EDIT_CFG_JSON', str(settings_file))
    editor = chosen_ui('dump')._replace(home_settings='.edit-cfg-json-tk.cfg')
    # pylint: disable-next=protected-access
    settings = edit_cfg._session_settings(editor, sys.stderr)
    assert (settings.backup_count, settings.file_extension) == (3, '.cfg')
