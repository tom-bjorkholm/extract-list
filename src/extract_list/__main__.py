#! /usr/local/bin/python3
# PYTHON_ARGCOMPLETE_OK
"""Extract a list of columns from JSON or XML and save to excel, CSV, etc."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

import sys
from extract_list.extract_cmd import extract_cmd  # pragma: no cover # noqa: E501

if __name__ == '__main__':  # pragma: no cover
    sys.exit(extract_cmd())
