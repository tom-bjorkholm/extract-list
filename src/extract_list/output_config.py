#! /usr/local/bin/python3
"""Unified output configuration for extract-list."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional, TextIO, override
import sys
from config_as_json import CharEncodingValidator, Config, \
    MemberValidationStep, OptionalMemberValidator, PathOrStr, StrValidator, \
    ValidationPlan, ValueTypeValidator
from tableio import Capabilities, FileAccess
from tableio_cfg_json import TioJsonConfig
from extract_list.config_enums import INTERNAL_OUTFILE_FORMATS, \
    is_internal_out_file_format


class ExtractOutputConfig(TioJsonConfig):
    """Configuration for one extract-list output format."""

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, capabilities: Capabilities, file_access: FileAccess,
                 format_name: Optional[str] = None,
                 implementation: Optional[str] = None,
                 include_all_options: bool = False,
                 from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[PathOrStr] = None,
                 allowed_formats: Optional[list[str]] = None,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Create output settings or read them from a JSON source."""
        internal = format_name is not None and \
            is_internal_out_file_format(format_name)
        init_format = None if internal else format_name
        init_impl = None if internal else implementation
        self._allowed_formats = allowed_formats
        super().__init__(capabilities=capabilities, file_access=file_access,
                         format_name=init_format, implementation=init_impl,
                         include_all_options=include_all_options,
                         from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename,
                         stderr_file=stderr_file)
        if internal and from_json_data_text is None and \
                from_json_filename is None:
            assert format_name is not None
            self.format_name = format_name
            self.implementation = implementation
            self.validate(stderr_file=stderr_file)

    def _format_names(self) -> list[str]:
        """Return internal output formats allowed for this configuration."""
        if self._allowed_formats is not None:
            return [
                value for value in self._allowed_formats
                if is_internal_out_file_format(value)]
        return INTERNAL_OUTFILE_FORMATS.copy()

    @override
    def get_validation_plan(self, stderr_file: TextIO) -> ValidationPlan:
        """Return validation for unified output settings."""
        if not is_internal_out_file_format(self.format_name):
            return TioJsonConfig.get_validation_plan(self, stderr_file)
        _ = stderr_file
        optional_string = OptionalMemberValidator(ValueTypeValidator(str))
        optional_impl = OptionalMemberValidator(StrValidator(
            allowed_values=['internal'], ignore_case=True, best_match=True,
            normalize=True))
        optional_int = OptionalMemberValidator(ValueTypeValidator(int))
        optional_encoding = OptionalMemberValidator(CharEncodingValidator())
        return [
            MemberValidationStep(member_names=['format_name'],
                                 validator=StrValidator(
                                     allowed_values=self._format_names(),
                                     ignore_case=True, best_match=True,
                                     normalize=True)),
            MemberValidationStep(member_names=['implementation'],
                                 validator=optional_impl),
            MemberValidationStep(member_names=['language', 'title',
                                               'paper_size',
                                               'table_alignment'],
                                 validator=optional_string),
            MemberValidationStep(member_names=['character_encoding'],
                                 validator=optional_encoding),
            MemberValidationStep(member_names=['line_length',
                                               'table_max_line_length'],
                                 validator=optional_int)
        ]

    @override
    def validate(self, stderr_file: TextIO) -> None:
        """Validate internal output or the TableIO output configuration."""
        if is_internal_out_file_format(self.format_name):
            Config.validate(self, stderr_file=stderr_file)
            return
        TioJsonConfig.validate(self, stderr_file=stderr_file)
