#! /usr/local/bin/python3
"""Generate text describing example configuration."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

from typing import TextIO
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt_syntax import generate_syntax_txt

# pylint: disable=duplicate-code


def generate_txt_example_json(file: TextIO, cfgtype: CfgTypes,
                              outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype == CfgTypes.EXAMPLE_JSON
    msg = f'''
    This is an example created especially to demonstrate how to use the
    configuration file with extract_list. The example will create an
    output file in {outtype.name} format.'''
    msg += '''
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
          "items": [
            { "item": "apple", "quantity": 5 }
          ],
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
      }
    }

    Here we choose "orders" to be the path of to the main line.
    The dictionary key directly following "orders" will be included in the
    output with the column name "key col".
    We give the name "What" to the relative path ["items", "item"] in the
    main line record. We give the name "How many" to the relative path
    ["items", "item"] in the main line record.
    We notice that as each orders may contain several items we need to
    do "expand_at" the relative path ["items"] to be able to include
    the purchased items in the list of columns we have as output format.

    We choose customers as the single linked line in "linked_lines".
    We give the name "Customer name" to the relative path ["name"] in the
    linked line record. We give the name "Street" to the relative path
    ["address", "street"] in the linked line record. We give the name
    "Street number" to the relative path ["address", "number"] in the
    linked line record. We do not want any "expand_at" in the linked
    line record so we specify "expand_at" as an empty list.
    The relative path ["customer number"] in the linked line records
    is tied to the relative path ["customer"] in the main line records,
    using "linked_column" with value ["customer number"] and
    "linked_main_column" with value ["customer"].

    If the path for any column does not exist in the input data, that
    column will be given an empty value (instead of seeing it as an
    error).

    "one_output_line_per_main_line" is set to true, meaning that
    it will be an error if several linked lines map to the same
    main line.

    '''
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0
