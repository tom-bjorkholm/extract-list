#! /usr/local/bin/python3
"""Version reporting for extract-list."""

# Copyright (c) 2024 - 2026 Tom Björkholm
# MIT License

from datetime import date
from packaging.version import Version
from versionreporter import VersionReporter, SupportExpires


class XlVersion(VersionReporter):
    """Get and print version information."""

    def package_names(self) -> list[str]:
        """Get list of main package names."""
        return ['extract_list', 'config_as_json', 'tableio',
                'tableio-cfg-json', 'versionreporter', 'xmltodict']

    @classmethod
    def get_main_package_name(cls) -> str:
        """Get the main package name."""
        return 'extract-list'

    @classmethod
    def recommended_python(cls) -> Version:
        """Get recommended Python version."""
        return Version('3.14')

    def get_app_support_expires(self) -> SupportExpires:
        """Get the Python-version support cutoffs for the application.

        Returns:
        dict[date, str]: Mapping from support-end dates to the highest
                         unsupported Python major.minor version.
        """
        support_end = {date(year=2025, month=12, day=1): '3.11',
                       date(year=2026, month=3, day=1): '3.12',
                       date(year=2027, month=10, day=1): '3.13'}
        return support_end
