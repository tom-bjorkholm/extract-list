#! /usr/local/bin/python3
"""Test output format enumeration helpers."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional
import pytest
from tableio import CAP_IGNORABLE, CAP_NEEDED, CAP_NOT_USED, Capabilities
from tableio.capability import SingleCapability
from extract_list import config_enums
from extract_list.config_enums import FormatRequest, \
    INTERNAL_OUTFILE_FORMATS, get_outfile_capabilities, \
    list_out_file_formats, list_out_format_implementations
from .check_capsys import check_capsys


@pytest.mark.parametrize('fmt_request, expected',
                         [(FormatRequest.NO, CAP_NOT_USED),
                          (FormatRequest.IF_AVAILABLE, CAP_IGNORABLE),
                          (FormatRequest.NEEDED, CAP_NEEDED)])
def test_format_cap_matrix(capsys: pytest.CaptureFixture[str],
                           fmt_request: FormatRequest,
                           expected: SingleCapability) -> None:
    """Test mapping from output feature request to TableIO capability."""
    capabilities = get_outfile_capabilities(border=fmt_request,
                                            filtered_area=fmt_request)
    assert capabilities.can_write == CAP_NEEDED
    assert capabilities.can_read == CAP_NOT_USED
    assert capabilities.can_write_borders == expected
    assert capabilities.filtered_data_range == expected
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('border, filtered_area, internal',
                         [(FormatRequest.NO, FormatRequest.NO, True),
                          (FormatRequest.IF_AVAILABLE, FormatRequest.NO, True),
                          (FormatRequest.NO, FormatRequest.IF_AVAILABLE, True),
                          (FormatRequest.NEEDED, FormatRequest.NO, False),
                          (FormatRequest.NO, FormatRequest.NEEDED, False),
                          (FormatRequest.NEEDED, FormatRequest.NEEDED, False)])
def test_out_format_matrix(capsys: pytest.CaptureFixture[str],
                           monkeypatch: pytest.MonkeyPatch,
                           border: FormatRequest, filtered_area: FormatRequest,
                           internal: bool) -> None:
    """Test internal output formats against feature request combinations."""
    cap_calls: list[Capabilities] = []

    def fake_registered(capabilities: Capabilities,
                        empty_is_ok: bool) -> list[str]:
        """Return deterministic fake TableIO formats."""
        assert empty_is_ok
        cap_calls.append(capabilities)
        return ['TableIO']

    monkeypatch.setattr(config_enums, 'list_registered_tableio',
                        fake_registered)
    formats = list_out_file_formats(border=border, filtered_area=filtered_area)
    expected = ['TableIO']
    if internal:
        expected.extend(INTERNAL_OUTFILE_FORMATS)
    assert formats == expected
    assert len(cap_calls) == 1
    assert cap_calls[0].can_write_borders == \
        get_outfile_capabilities(border=border).can_write_borders
    check_capsys(capsys=capsys)


@pytest.mark.parametrize('case',
                         [(None, FormatRequest.NO, FormatRequest.NO,
                           ['tableio', 'internal'], True),
                          (None, FormatRequest.NEEDED,
                           FormatRequest.IF_AVAILABLE, ['tableio'], True),
                          ('CSV', FormatRequest.NEEDED,
                           FormatRequest.IF_AVAILABLE, ['tableio'], True),
                          ('json', FormatRequest.NO, FormatRequest.NO,
                           ['internal'], False),
                          ('json', FormatRequest.NEEDED, FormatRequest.NO,
                           [], False)])
def test_impl_list_matrix(capsys: pytest.CaptureFixture[str],
                          monkeypatch: pytest.MonkeyPatch,
                          case: tuple[Optional[str], FormatRequest,
                                      FormatRequest, list[str], bool]) -> None:
    """Test implementation list behavior for internal and TableIO formats."""
    format_name, border, filtered_area, expected, called = case
    called_formats: list[Optional[str]] = []

    def fake_implementations(format_name: Optional[str],
                             capabilities: Capabilities,
                             empty_is_ok: bool) -> list[str]:
        """Return deterministic fake TableIO implementations."""
        assert empty_is_ok
        assert capabilities.can_write == CAP_NEEDED
        called_formats.append(format_name)
        return ['tableio']

    monkeypatch.setattr(config_enums, 'list_implementations_tableio',
                        fake_implementations)
    implementations = list_out_format_implementations(format_name, border,
                                                      filtered_area)
    assert implementations == expected
    if called:
        assert called_formats == [format_name]
    else:
        assert not called_formats
    check_capsys(capsys=capsys)
