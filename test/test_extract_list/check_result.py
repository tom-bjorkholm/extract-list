#! /usr/local/bin/python3
"""Check that two resulting data sets are equal."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from extract_list.commontypes import Data, Row, Value

ex_res: Data = [
    {'What': 'apple', 'How many': 5, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '123'},
    {'What': 'banana', 'How many': 1, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'key col': '234'},
    {'What': 'carrot', 'How many': 2, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '345'},
    {'What': 'orange', 'How many': 6, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'key col': '234'},
    {'What': 'orange', 'How many': 70, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'key col': '345'}
]

ex2_res: Data = [
    {'What': 'apple', 'How many': 5, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'Deliver by': 'car'},
    {'What': 'banana', 'How many': 1, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'Deliver by': 'bike'},
    {'What': 'carrot', 'How many': 2, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'Deliver by': 'car'},
    {'What': 'orange', 'How many': 6, 'Customer name': 'Mickey Mouse',
     'Street': 'Another Street', 'Street number': 7, 'Deliver by': 'bike'},
    {'What': 'orange', 'How many': 70, 'Customer name': 'Donald Duck',
     'Street': 'Some Road', 'Street number': 666, 'Deliver by': 'car'}
]


def _check_value_equal(*,  # pylint: disable=too-many-arguments
                       res_val: Value, other_val: Value, key: str,
                       res_row: Row, other_row: Row, res_data: Data,
                       other_data: Data, turned: bool = False) -> None:
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
                           key=key, res_row=res_row, other_row=other_row,
                           res_data=res_data, other_data=other_data,
                           turned=True)
        return
    assert res_val == other_val, \
        f'Key "{key}" has different values {res_val} != {other_val}' +\
        f'\n  res_row={res_row}\nother_row={other_row}\n' +\
        f'  res_data={res_data}\nother_data={other_data}'


def check_result(result_data: Data,  # pylint: disable=dangerous-default-value # noqa: E501
                 other_result: Data) -> None:
    """Check if result data equals other result data."""
    assert isinstance(result_data, list)
    assert isinstance(other_result, list)
    assert len(result_data) == len(other_result)
    if len(result_data) == 0:
        return
    keys = sorted(list(result_data[0].keys()))
    for i, row in enumerate(result_data):
        rowkeys = sorted(list(row.keys()))
        assert keys == rowkeys, \
            f'Keys differ in result row {i}\n{keys} != {rowkeys}'
    for i, row in enumerate(other_result):
        rowkeys = sorted(list(row.keys()))
        assert keys == rowkeys, \
            f'Keys differ in expected row {i}\n{keys} != {rowkeys}'
    for res_row, other_row in zip(result_data, other_result):
        for key in keys:
            _check_value_equal(res_val=res_row[key], other_val=other_row[key],
                               key=key, res_row=res_row, other_row=other_row,
                               res_data=result_data, other_data=other_result)
