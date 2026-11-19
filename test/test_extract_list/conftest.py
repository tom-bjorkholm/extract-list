#! /usr/bin/env python3
"""Pytest configuration for extract_list tests."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

import tkinter
import pytest


def tk_description() -> str:
    """Describe the Tk that the tests run on, or say there is no display.

    The exact Tk version and the windowing system are only known once
    Tk has opened a display, so without one only its major and minor
    version are told.
    """
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return f'Tk {tkinter.TkVersion} (no display)'
    root.withdraw()
    patch_level = root.getvar('tk_patchLevel')
    system = root.call('tk', 'windowingsystem')
    root.destroy()
    return f'Tk {patch_level}, windowing system {system}'


def pytest_report_header() -> str:
    """Tell which Tcl/Tk the tests run on, to help explain Tk failures."""
    tcl_level = tkinter.Tcl().call('info', 'patchlevel')
    return f'tcl/tk: Tcl {tcl_level}, {tk_description()}'


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers for backlogops_gui tests."""
    config.addinivalue_line(
        'markers',
        'focus_sensitive: test requires a focused window and unlocked '
        'display; run manually under controlled conditions')
