#! /usr/local/bin/python3
"""Build reported paths of elements in a nested configuration."""

# Copyright (c) 2026 Tom Björkholm
# MIT License


def element_path(member_name: str, index: int | str) -> str:
    """Return the reported path of one list element or dict value.

    Indexing into a list or a dict appends the index or the key in
    square brackets, which is the notation config-as-json uses in
    diagnostics. Going into an attribute instead appends a dot and the
    attribute name, which is what config_as_json.member_path does.

    Args:
        member_name: Reported path of the list or dict itself.
        index: List index or dict key of the element.

    Returns:
        The reported path of the element, such as ``linked_lines[1]``.
    """
    return f'{member_name}[{index}]'
