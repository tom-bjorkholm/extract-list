#! /usr/local/bin/python3
"""Edit an extract-list configuration file in an interactive editor.

The editor is the edit-cfg-json family: it opens in whichever installed user
interface can run here (a window where there is a display, the terminal
where there is none), unless the user names one.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from dataclasses import replace
from typing import Optional, TextIO
import io
from config_as_json import Config
from config_as_json.file_extension import fix_file_extension
from config_as_json.file_must_exist import file_must_exist
from edit_cfg_json import ConfigLoadError, NoEditorError, Settings, \
    UiBackend, chosen_ui, edit_in_ui, load_settings
from extract_list.cfg_descriptions import extract_descriptions
from extract_list.extract_config import ExtractConfig

CFG_EXTENSION = '.cfg'
"""File extension of extract-list configuration files."""

NO_INPUT_HINT = ('To get a configuration file to start from, use the '
                 '"cfg-example" sub-command.')
"""What a user who named no existing configuration file is told to do."""


def _chosen_editor(ui_name: Optional[str]) -> UiBackend:
    """Return the user interface to edit in.

    As in the edit-cfg-json program, the choice is made with the settings
    shared by all editors, so that ui_priorities in the user's settings
    decides when ui_name is None. Notes about an old settings file format
    are silenced here, as the session settings read the same file again.

    Raises:
        ConfigLoadError: The settings file cannot be read.
        NoEditorError: ui_name cannot run here, or no editor can.
    """
    choosing = load_settings(stderr_file=io.StringIO())
    return chosen_ui(ui_name=ui_name, settings=choosing)


def _session_settings(editor: UiBackend, stderr_file: TextIO) -> Settings:
    """Return the user's settings for the editor, saving as .cfg files.

    The lookup is the one of the edit-cfg-json programs: the file named by
    the CFG_EDIT_CFG_JSON environment variable, then the chosen editor's own
    file in the home folder (such as .edit-cfg-json-tk.cfg), then
    .edit-cfg-json.cfg in the home folder, and else the defaults. Only the
    file extension is decided by extract-list.

    Raises:
        ConfigLoadError: The settings file cannot be read.
    """
    found = load_settings(home_settings=editor.home_settings,
                          stderr_file=stderr_file)
    return replace(found, file_extension=CFG_EXTENSION)


def _existing_input(in_file: str, stderr_file: TextIO) -> Optional[str]:
    """Return the configuration file to read, or None if there is none.

    As for the extract sub-command, ".cfg" is added to a name that does
    not exist as written. A missing file is explained on stderr_file.
    """
    fixed = fix_file_extension(filename=in_file, ext_to_add=CFG_EXTENSION,
                               for_reading=True)
    try:
        file_must_exist(filename=fixed, with_content_txt='configuration',
                        stderr_file=stderr_file, exit_if_missing=False)
    except FileNotFoundError:
        print(NO_INPUT_HINT, file=stderr_file)
        return None
    return fixed


def _edit(in_file: str, out_file: Optional[str], ui_name: Optional[str],
          stderr_file: TextIO) -> Optional[Config]:
    """Run one editing session and return what was saved, or None.

    Raises:
        ConfigLoadError: A file cannot be read, or holds invalid values.
        NoEditorError: ui_name cannot run here, or no editor can.
    """
    editor = _chosen_editor(ui_name)
    return edit_in_ui(ExtractConfig(stderr_file=stderr_file),
                      ui_name=editor.ui_name,
                      descriptions=extract_descriptions(), in_file=in_file,
                      out_file=out_file,
                      settings=_session_settings(editor, stderr_file),
                      stderr_file=stderr_file)


def edit_cfg_func(in_file: str, out_file: Optional[str],
                  ui_name: Optional[str], stderr_file: TextIO) -> int:
    """Edit a configuration file and return the exit code of the command.

    Args:
        in_file: Configuration file to edit. It must exist.
        out_file: File to save to, or None to save to in_file.
        ui_name: User interface to edit in, or None for the best one here.
        stderr_file: Stream for user-facing diagnostics.

    Returns:
        0 when the session ended normally, saved or not, and 1 when no
        editing session could be opened.
    """
    existing = _existing_input(in_file, stderr_file)
    if existing is None:
        return 1
    try:
        saved = _edit(existing, out_file, ui_name, stderr_file)
    except (ConfigLoadError, NoEditorError) as refusal:
        print(refusal, file=stderr_file)
        return 1
    if saved is None:
        print('Nothing was saved.')
    return 0
