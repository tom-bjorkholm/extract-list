#! /usr/local/bin/python3
"""Text describing example configuration for both JSON and XML."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

ORDERS_KEY_COL = '''
The dictionary key directly following "orders" will be included in the
output with the column name "key col".'''

ORDERS_COLUMNS = '''
We give the name "What" to the relative path ["items", "item"] in the
main line record. We give the name "How many" to the relative path
["items", "item"] in the main line record.
We notice that as each orders may contain several items we need to
do "expand_at" the relative path ["items"] to be able to include
the purchased items in the list of columns we have as output format.
'''

EX1_ORDERS = ORDERS_KEY_COL + ORDERS_COLUMNS

CUSTOMERS_COLUMNS = '''
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

'''

NONEXIST_EMPTY = '''
If the path for any column does not exist in the input data, that
column will be given an empty value (instead of seeing it as an
error).

'''

ONE_PER_MAIN = '''
"one_output_line_per_main_line" is set to true, meaning that
it will be an error if several linked lines map to the same
main line.
'''

EX1_CUST_AND_REST = CUSTOMERS_COLUMNS + NONEXIST_EMPTY + ONE_PER_MAIN

# TODO make correct description for example 2

EX2_ORDERS = ORDERS_COLUMNS
EX2_CUST_AND_REST = EX1_CUST_AND_REST
