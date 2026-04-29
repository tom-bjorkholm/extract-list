#! /usr/local/bin/python3
"""Warn users when backward compatibility was needed during parsing."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import sys
from config_as_json.migrate_cfg_warn_hook import MigrateCfgWarnHook


class XlMigrateCfgWarnHook(MigrateCfgWarnHook):
    """Migrate configuration file to new format."""

    @classmethod
    def migrate_instructions(cls) -> str:
        """Return instructions for migrating the configuration file."""
        python = 'python3'
        if sys.platform.lower() == 'win32' or sys.platform.lower() == 'nt':
            python = 'python'
        txt = f'Use "{python} -m extract_list migrate-cfg" to migrate the\n'
        txt += 'configuration file to the new format.\n\n'
        return txt
