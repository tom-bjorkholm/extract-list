#! /usr/local/bin/python3
"""Test expand_line in extract_data."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
import pytest
from config_as_json import JsonType
from extract_list.extract_data import expand_line, set_at_path
from .check_capsys import check_capsys


@pytest.mark.parametrize('dat,pth,newdat,res',
                         [({'b': 'c', 'd': 'e'}, ['d'], 'nn',
                           {'b': 'c', 'd': 'nn'}),
                          ({'a': [{'b': 'c1'}, {'b': 'c2'}]},
                           ['a'], {'b': 'c2'},
                           {'a': {'b': 'c2'}}),
                          ({'a': 'b', 'c': {'d': 'e', 'k': 'm'}}, ['c', 'd'],
                           {'f': 'g'},
                           {'a': 'b', 'c': {'d': {'f': 'g'}, 'k': 'm'}})])
def test_set_at_path_ok1(capsys: pytest.CaptureFixture[str], dat: JsonType,
                         pth: list[str], newdat: JsonType,
                         res: JsonType) -> None:
    """Test OK cases 1 of set_at_path."""
    localdata = deepcopy(dat)
    set_at_path(data=localdata, path=deepcopy(pth), newdata=deepcopy(newdat))
    check_capsys(capsys=capsys)
    assert localdata == res


@pytest.mark.parametrize('skey', ['abc'])
@pytest.mark.parametrize('dlin, expa, res',
                         [({'a': [{'b': 'c1'}, {'b': 'c2'}]}, [['a']],
                           [{'a': {'b': 'c1'}}, {'a': {'b': 'c2'}}]),
                          ({'items': [{'item': 'Orange', 'quantity': 1},
                           {'item': 'Banana', 'quantity': 6}],
                            'customer': 22},
                           [['items']],
                           [{'items': {'item': 'Orange', 'quantity': 1},
                             'customer': 22},
                            {'items': {'item': 'Banana', 'quantity': 6},
                             'customer': 22}]
                           )])
def test_expand_line_ok1(capsys: pytest.CaptureFixture[str], skey: str,
                         dlin: JsonType, expa: list[list[str]],
                         res: list[JsonType]) -> None:
    """Test OK cases 1 of expand_line."""
    ret = []
    for key, value in expand_line(skey=deepcopy(skey), dline=deepcopy(dlin),
                                  expand=deepcopy(expa)):
        assert key == skey
        ret.append(value)
    check_capsys(capsys=capsys)
    assert len(ret) == len(res)
    for elem in ret:
        assert elem in res
