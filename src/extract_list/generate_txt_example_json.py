#! /usr/local/bin/python3
"""Generate text describing example configuration."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import TextIO
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt_syntax import generate_syntax_txt
from extract_list.generate_txt_ex_common import \
    EX1_ORDERS, EX1_CUST_AND_REST, EX2_ORDERS, EX2_CUST_AND_REST


EXAMPLE_JSON = '''
This example is based on JSON input data in this format:

{
  "customers": [
    {
      "name": "Donald Duck",
      "address": { "street": "Some Road", "number": 666 },
      "customer_number": 66
    },
    {
      "name": "Mickey Mouse",
      "address": { "street": "Another Street", "number": 7 },
      "customer_number": 22
    }
  ],
  "orders": {
    "123": {
      "items": [ { "item": "apple", "quantity": 5 } ],
      "customer": 66
    },
    "234": {
      "items": [
        { "item": "banana", "quantity": 1 },
        { "item": "orange", "quantity": 6 }
      ],
      "customer": 22
    },
    "345": {
      "items": [
        { "item": "carrot", "quantity": 2 },
        { "item": "orange", "quantity": 20 }
      ],
      "customer": 66
    }
  },
  "delivery_method": [
    { "for_street": "Another Street", "deliver_by": "bike" },
    { "for_street": "Some Road", "deliver_by": "car" }
  ]
}

'''

ORDERS_LINE_JSON = '''

Here we choose "orders" to be the path of to the main line.'''

CUST_LINE_JSON = '''
We choose "customers" as the single linked line in "linked_lines". '''


def generate_txt_example_json(file: TextIO, cfgtype: CfgTypes,
                              outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype == CfgTypes.EXAMPLE_JSON
    msg = f'''
    This is an example created especially to demonstrate how to use the
    configuration file with extract_list. The example will create an
    output file in {outtype.name} format.'''
    msg += EXAMPLE_JSON + ORDERS_LINE_JSON + EX1_ORDERS
    msg += CUST_LINE_JSON + EX1_CUST_AND_REST
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0


def generate_txt_example2_json(file: TextIO, cfgtype: CfgTypes,
                               outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype == CfgTypes.EXAMPLE2_JSON
    msg = f'''
    This is another example created especially to demonstrate how to use the
    configuration file with extract_list. The example will create an
    output file in {outtype.name} format.'''
    msg += EXAMPLE_JSON + ORDERS_LINE_JSON + EX2_ORDERS
    # TODO make correct description for example 2
    msg += CUST_LINE_JSON + EX2_CUST_AND_REST
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0
