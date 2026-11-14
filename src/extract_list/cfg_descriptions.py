#! /usr/local/bin/python3
"""Descriptions of the configuration members, shown by the editor.

The configuration editor shows the description of a member below it, so
these texts are the help a user gets while editing. They are keyed by the
absolute path of the member, and the step '[' means every element of a list
or every value of a dict at that point.

The members of the nested "output" object are described by tableio-cfg-json
itself, so that their texts follow TableIO. Only where extract-list adds
something of its own (the JSON, XML and Plaintxt formats) is that text
replaced or extended here.
"""

# Copyright (c) 2026 Tom Björkholm
# MIT License

from config_as_json import ConfigPath
from edit_cfg_json import Descriptions
from tableio_cfg_json import tio_json_descriptions
from extract_list.config_enums import INTERNAL_OUTFILE_FORMATS, \
    list_out_file_formats

EVERY = '['
"""Path step selecting every element of a list or value of a dict."""

PATH_STEP = ('One key of the path, in order from the outside in. A key is '
             'the name of a JSON object member or of an XML element.')
"""Description of one step of any path in the configuration."""

_TOP_LEVEL: dict[ConfigPath, str] = {
    ('infile_type',):
        'Format of the input file that data is extracted from.',
    ('infile_encoding',):
        'Character encoding of the input file, such as utf-8, cp1252 or '
        'iso-8859-1. Keep utf-8 unless you know that the input file is '
        'written in another encoding.',
    ('in_xml_strip_at',):
        'Only used for XML input. XML attributes are read with an "@" in '
        'front of their name, such as "@id". Set to true to remove that '
        '"@", so that the paths of this configuration name attributes '
        'without it.',
    ('include_key',):
        'Whether the output gets a column holding the key of each main line '
        'record: the dictionary key, or the list index, that the record has '
        'at main_line.line. The column is named by column_name_for_key.',
    ('column_name_for_key',):
        'Name of the output column holding the key of each main line '
        'record. Only used when include_key is true. Like every extracted '
        'column it must also be listed in column_order.',
    ('missing_input_for_column',):
        'What to do when a record has no value at the path of a column. '
        'EMPTY leaves that cell empty, which suits input where records may '
        'leave out optional items. ERROR stops the extraction with a '
        'message, which helps to find misspelled paths.',
    ('main_line',):
        'The records that become the lines of the output, such as the '
        'orders of an order file. Each record found at "line" gives one '
        'output line, or several when "expand_at" splits it. Data from '
        'linked lines is added to these lines.',
    ('linked_lines',):
        'Other records whose data is added to the main line record they are '
        'linked to, such as the customer of each order. Leave empty when '
        'all data is in the main line records. A new element starts empty: '
        'fill in at least its line, columns and how it is linked.',
    ('linked_lines', EVERY):
        'One kind of linked record, and how it is linked to the main line. '
        'A linked record belongs to a main line record when its value at '
        'linked_column equals the value of the main line record at '
        'linked_main_column.',
    ('one_output_line_per_main_line',):
        'What to do when several linked records are linked to one main line '
        'record. true: that is an error, so each main line record gives '
        'exactly one output line. false: the main line record is repeated '
        'on one output line per linked record, such as one line per order '
        'of a customer.',
    ('outfile_border',):
        'Whether the cells of the output table get borders. NO: no borders. '
        'IF_AVAILABLE: borders where the output format and implementation '
        'can draw them. NEEDED: only output formats that can draw borders '
        'are allowed, which rules out JSON, XML and Plaintxt.',
    ('outfile_filtered_area',):
        'Whether the output table is marked as a filterable data range, such '
        'as a filter on the header row of a spreadsheet. NO: no filter. '
        'IF_AVAILABLE: a filter where the output format and implementation '
        'support one. NEEDED: only output formats that support a filter are '
        'allowed, which rules out JSON, XML and Plaintxt.',
    ('output',):
        'Format of the output file and its options. Most options are only '
        'used by some formats, and each of them says which.',
    ('column_order',):
        'Order of the columns in the output, by column name. It must hold '
        'every extracted column exactly once and nothing else: every name '
        'in main_line.columns and in the columns of each linked line, and '
        'column_name_for_key when include_key is true. For XML output the '
        'names become element names and must not contain whitespace.',
    ('column_order', EVERY):
        'Name of one extracted column. Its place in this list is its place '
        'in the output.',
    ('order_rows_by',):
        'Columns to sort the output lines by, most significant first. Leave '
        'empty to sort by the columns of column_order, in that order.',
    ('order_rows_by', EVERY):
        'Name of one extracted column to sort by.',
    ('out_xml_attributes',):
        'Only used for XML output. Columns to write as XML attributes of the '
        'element of each output line, rather than as nested elements.',
    ('out_xml_attributes', EVERY):
        'Name of one extracted column to write as an XML attribute.'
}
"""Descriptions of the members at the top level of the configuration."""

_LINE_SPEC: dict[ConfigPath, str] = {
    ('line',):
        'Path from the top of the input file to the records, one key per '
        'element. What is found there must be a list or a dictionary of '
        'records. Example: ["orders"] for {"orders": {"o1": {...}}}. For XML '
        'input the path starts with the root element, such as '
        '["data", "orders", "order"].',
    ('line', EVERY): PATH_STEP,
    ('columns',):
        'Output columns taken from each record. The name of each entry is '
        'the column name in the output, and its value is the path to the '
        'value inside the record. Column names must be unique across the '
        'main line, the linked lines and the key column, and each must be '
        'listed in column_order.',
    ('columns', EVERY):
        'Path inside the record to the value of this column, one key per '
        'element, such as ["address", "street"] for '
        '{"address": {"street": "Main St"}}. The name of this entry is the '
        'column name in the output.',
    ('columns', EVERY, EVERY): PATH_STEP,
    ('expand_at',):
        'Paths inside the record to lists that are split into one output '
        'line per list element, such as ["items"] for an order holding '
        'several items. The rest of the record is repeated on each of these '
        'lines. Leave empty when each record gives one output line.',
    ('expand_at', EVERY):
        'Path inside the record to one list that is split into one output '
        'line per element. A column path through this path continues inside '
        'the element, such as ["items", "quantity"] for ["items"].',
    ('expand_at', EVERY, EVERY): PATH_STEP
}
"""Descriptions of the members of main_line and of each linked line."""

_LINK: dict[ConfigPath, str] = {
    ('linked_main_column',):
        'Path inside the main line record to the value that links it, such '
        'as ["customer"]. A linked record is linked to it when the value at '
        'linked_column in the linked record is equal.',
    ('linked_main_column', EVERY): PATH_STEP,
    ('linked_column',):
        'Path inside this linked record to the value that must equal the '
        'value at linked_main_column in the main line record, such as '
        '["customer_number"].',
    ('linked_column', EVERY): PATH_STEP
}
"""Descriptions of the members only a linked line has."""


def _under(prefix: ConfigPath,
           relative: dict[ConfigPath, str]) -> dict[ConfigPath, str]:
    """Return the descriptions with the prefix put before every path."""
    return {prefix + path: text for path, text in relative.items()}


def _output_descriptions() -> dict[ConfigPath, str]:
    """Return descriptions of the nested output object.

    The TableIO texts are used as they are, except for the members where
    extract-list's own formats add choices TableIO does not know about.
    """
    tio = dict(tio_json_descriptions(('output',)))
    internal = ', '.join(INTERNAL_OUTFILE_FORMATS)
    tio[('output', 'format_name')] = (
        'Format of the output file. With outfile_border and '
        'outfile_filtered_area set to NO the choices are: '
        + ', '.join(list_out_file_formats()) + '. '
        + internal + ' are written by extract-list itself, the others by '
        'TableIO. Asking for borders or a filter as NEEDED removes the '
        'formats that cannot provide them.')
    tio[('output', 'implementation')] += (
        f'\nFor {internal} the only implementation is "internal", which may '
        'also be left as None.')
    tio[('output', 'character_encoding')] += (
        f'\n{internal} output also uses this encoding, and utf-8 when None.')
    return tio


def extract_descriptions() -> Descriptions:
    """Return what the editor shows about every configuration member.

    It is built when asked for, because the output formats it lists depend
    on which TableIO formats are installed.
    """
    return {**_TOP_LEVEL, **_under(('main_line',), _LINE_SPEC),
            **_under(('linked_lines', EVERY), _LINE_SPEC),
            **_under(('linked_lines', EVERY), _LINK),
            **_output_descriptions()}
