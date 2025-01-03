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

EXAMPLE_XML = '''
This example is based on XML input data in this format:

<?xml version="1.0" encoding="utf-8"?>
<data>
    <customers>
        <name>Donald Duck</name>
        <address>
            <street>Some Road</street>
            <number>666</number>
        </address>
        <customer_number>66</customer_number>
    </customers>
    <customers>
        <name>Mickey Mouse</name>
        <address>
            <street>Another Street</street>
            <number>7</number>
        </address>
        <customer_number>22</customer_number>
    </customers>
    <orders>
        <i_123>
            <items>
                <item>apple</item>
                <quantity>5</quantity>
            </items>
            <customer>66</customer>
        </i_123>
        <i_234>
            <items>
                <item>banana</item>
                <quantity>1</quantity>
            </items>
            <items>
                <item>orange</item>
                <quantity>6</quantity>
            </items>
            <customer>22</customer>
        </i_234>
        <i_345>
            <items>
                <item>carrot</item>
                <quantity>2</quantity>
            </items>
            <items>
                <item>orange</item>
                <quantity>20</quantity>
            </items>
            <customer>66</customer>
        </i_345>
    </orders>
    <delivery_method>
        <for_street>Another Street</for_street>
        <deliver_by>bike</deliver_by>
    </delivery_method>
    <delivery_method>
        <for_street>Some Road</for_street>
        <deliver_by>car</deliver_by>
    </delivery_method>
</data>
'''

ORDERS_LINE_XML = '''

Here we choose ["data", "orders"] to be the path of to the main line.'''

CUST_LINE_XML = '''
We choose ["data", "customers"] as the single linked line in
"linked_lines". '''


def generate_txt_example_xml(file: TextIO, cfgtype: CfgTypes,
                             outtype: OutFileType) -> int:
    """Write text describing configuration example_xml."""
    assert cfgtype == CfgTypes.EXAMPLE_XML
    msg = f'''
    This is an example created especially to demonstrate how to use the
    configuration file with extract_list. The example will create an
    output file in {outtype.name} format.'''
    msg += EXAMPLE_XML
    msg += ORDERS_LINE_XML + EX1_ORDERS
    msg += CUST_LINE_XML + EX1_CUST_AND_REST
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0


def generate_txt_example2_xml(file: TextIO, cfgtype: CfgTypes,
                              outtype: OutFileType) -> int:
    """Write text describing configuration example_xml."""
    assert cfgtype == CfgTypes.EXAMPLE2_XML
    msg = f'''
    This is another example created especially to demonstrate how to use the
    configuration file with extract_list. The example will create an
    output file in {outtype.name} format.'''
    msg += EXAMPLE_XML
    # TODO make correct description for example 2
    msg += ORDERS_LINE_XML + EX2_ORDERS
    msg += CUST_LINE_XML + EX2_CUST_AND_REST
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0
