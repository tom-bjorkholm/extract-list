#! /usr/local/bin/python3
"""Define validators for extract list."""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from typing import Optional, TextIO
import sys
from config_as_json import WholeConfigValidator, MemberValidator, \
    StrValidator, Config, InvalidConfiguration
from extract_list.optional_validator import OptionalMemberValidator
from extract_list.extract_config_params import ExtractConfigParams
from extract_list.config_enums import is_internal_out_file_format, \
    list_out_format_implementations


# pylint: disable-next=too-few-public-methods
class _OutputImplMemberValidator(MemberValidator):
    """Validate the configured output format implementation."""

    def validate_member(self, config: Config, member_name: str,
                        member_value: object,
                        stderr_file: TextIO = sys.stderr) -> Optional[object]:
        """Validate and normalize an optional implementation name."""
        assert isinstance(config, ExtractConfigParams)
        if is_internal_out_file_format(config.outfile_type):
            return None
        implementations = list_out_format_implementations(
            format_name=config.outfile_type, border=config.outfile_border,
            filtered_area=config.outfile_filtered_area)
        if not implementations:
            message = 'Invalid configuration: '
            message += f'No implementation can write {config.outfile_type}.'
            print(message, file=stderr_file)
            raise InvalidConfiguration(message)
        validator = StrValidator(allowed_values=implementations,
                                 ignore_case=True, best_match=True,
                                 normalize=True)
        return validator.validate_member(
            config=config, member_name=member_name,
            member_value=member_value, stderr_file=stderr_file)


# pylint: disable-next=too-few-public-methods
class OutputImplementationMemberValidator(OptionalMemberValidator):
    """Validate the configured optional output format implementation."""

    def __init__(self) -> None:
        """Construct validator."""
        super().__init__(validator=_OutputImplMemberValidator())


# pylint: disable-next=too-few-public-methods
class OutputImplementationValidator(WholeConfigValidator):
    """Validate the configured output format implementation."""

    def validate(self, config: Config,
                 stderr_file: TextIO = sys.stderr) -> None:
        """Validate and normalize the output format implementation."""
        assert isinstance(config, ExtractConfigParams)
        if is_internal_out_file_format(config.outfile_type):
            config.outfile_implementation = None
            return
        implementations = list_out_format_implementations(
            format_name=config.outfile_type, border=config.outfile_border,
            filtered_area=config.outfile_filtered_area)
        if not implementations:
            message = 'Invalid configuration: '
            message += f'No implementation can write {config.outfile_type}.'
            print(message, file=stderr_file)
            raise InvalidConfiguration(message)
