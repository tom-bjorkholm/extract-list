#! /usr/local/bin/python3
"""Check that two resulting data sets are equal."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from copy import deepcopy
from extract_list.commontypes import Data

ex_res: Data = [
    {'What': 'apple', 'How many': 5, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '123'},
    {'What': 'banana', 'How many': 1, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'key col': '234'},
    {'What': 'orange', 'How many': 6, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'key col': '234'},
    {'What': 'carrot', 'How many': 2, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '345'},
    {'What': 'orange', 'How many': 20, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '345'},
]


def _sorted_result(result_data: Data, sort_keys: list['str']):
    """Return a sorted version of data, sorted on all keys recursively."""
    if not sort_keys:
        return result_data
    data = sorted(deepcopy(result_data), key=lambda x: x[sort_keys[0]])
    if len(sort_keys) == 1:
        return data
    return _sorted_result(result_data=data, sort_keys=sort_keys[1:])


def _check_value_equal(res_val, other_val, key, turned=False):
    """Check if values are equal, allowing allowed differnces."""
    if res_val == other_val:
        return
    if isinstance(res_val, int) and isinstance(other_val, str):
        if str(res_val) == other_val:
            return
    if isinstance(other_val, str):
        if other_val[:2] == 'i_':
            if str(res_val) == other_val[2:]:
                return
    if not turned:
        _check_value_equal(res_val=other_val, other_val=res_val,
                           key=key, turned=True)
        return
    assert res_val == other_val, \
        f'Key "{key}" has different values {res_val} != {other_val}'


def check_result(result_data: Data,  # pylint: disable=dangerous-default-value # noqa: E501
                 other_result: Data = ex_res) -> None:
    """Check if result data equals other result data."""
    assert isinstance(result_data, list)
    assert isinstance(other_result, list)
    assert len(result_data) == len(other_result)
    if len(result_data) == 0:
        return
    keys = sorted(list(result_data[0].keys()))
    for i, row in enumerate(result_data):
        assert keys == sorted(list(row.keys())), \
            f'Keys differ in result row {i}'
    for i, row in enumerate(other_result):
        assert keys == sorted(list(row.keys())), \
            f'Keys differ in expected row {i}'
    res_data = _sorted_result(result_data=result_data, sort_keys=keys)
    other_data = _sorted_result(result_data=other_result, sort_keys=keys)
    for res_row, other_row in zip(res_data, other_data):
        for key in keys:
            _check_value_equal(res_val=res_row[key], other_val=other_row[key],
                               key=key)
