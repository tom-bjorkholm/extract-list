#! /usr/local/bin/python3
"""Example data for testing."""

# Copyright (c) 2024 Tom Björkholm
# MIT License

import json
import xmltodict


class ExampleData():
    """Example data for testing."""

    def __init__(self):
        """Construct example data."""
        self.data = \
            {
                'customers': [
                    {'name': 'Donald Duck',
                     'address': {'street': 'Some Road', 'number': 666},
                     'customer_number': 66},
                    {'name': 'Mickey Mouse',
                     'address': {'street': 'Another Stree', 'number': 7},
                     'customer_number': 22}
                ],
                'orders': {
                    '123': {'items': [{'item': 'apple', 'quantity': 5}],
                            'customer': 66},
                    '234': {'items': [{'item': 'banana', 'quantity': 1},
                                      {'item': 'orange', 'quantity': 6}],
                            'customer': 22},
                    '345': {'items': [{'item': 'carrot', 'quantity': 2},
                                      {'item': 'orange', 'quantity': 20}],
                            'customer': 66},
                }
            }

    @staticmethod
    def adjust_for_xml(data):
        """Adjust digit tags to non-digit."""
        if isinstance(data, list):
            ndata = []
            for row in data:
                nrow = ExampleData.adjust_for_xml(row)
                ndata.append(nrow)
            return ndata
        if isinstance(data, dict):
            ndata = {}
            for key, value in data.items():
                if isinstance(key, int):
                    nkey = 'i_' + str(key)
                    ndata[nkey] = ExampleData.adjust_for_xml(value)
                elif isinstance(key, str) and key.isdigit():
                    nkey = 'i_' + key
                    ndata[nkey] = ExampleData.adjust_for_xml(value)
                else:
                    ndata[key] = ExampleData.adjust_for_xml(value)
            return ndata
        return data

    @staticmethod
    def adjust_from_xml(data):
        """Reverse adjust_for_xml."""
        if isinstance(data, list):
            ndata = []
            for row in data:
                nrow = ExampleData.adjust_from_xml(row)
                ndata.append(nrow)
            return ndata
        if isinstance(data, dict):
            ndata = {}
            for key, value in data.items():
                if not isinstance(key, str):
                    ndata[key] = ExampleData.adjust_from_xml(value)
                    continue
                if len(key) < 3 or key[0:2] != 'i_':
                    ndata[key] = ExampleData.adjust_from_xml(value)
                    continue
                nkey = key[2:]
                ndata[nkey] = ExampleData.adjust_from_xml(value)
            return ndata
        return data

    def as_json_text(self) -> str:
        """Create JSON representation of data."""
        ret = json.dumps(self.data, indent=2)
        return ret

    def parse_json(self, txt: str) -> None:
        """Set internal data to the data parsed from JSON txt."""
        self.data = json.loads(txt)

    def as_xml_text(self) -> str:
        """Create XML representation of data."""
        data = self.adjust_for_xml(self.data)
        if len(self.data) > 1:
            data = {'data': data}
        ret = xmltodict.unparse(input_dict=data, pretty=True)
        return ret

    def parse_xml(self, txt: str) -> None:
        """Set internal data to the data parsed from XML txt."""
        print('\n\n\n\n From XML: \n')
        data = xmltodict.parse(xml_input=txt)
        if len(data) == 1 and 'data' in data:
            self.data = self.adjust_from_xml(data['data'])
        else:
            self.data = self.adjust_from_xml(data)

    def write_json_to_file(self, filename: str,
                           encoding: str = 'utf-8') -> None:
        """Write internal data to file as JSON text."""
        txt = self.as_json_text()
        with open(file=filename, mode='w', encoding=encoding) as file:
            file.write(txt)

    def write_xml_to_file(self, filename: str,
                          encoding: str = 'utf-8') -> None:
        """Write internal data to file as XML text."""
        txt = self.as_xml_text()
        with open(file=filename, mode='w', encoding=encoding) as file:
            file.write(txt)

    def read_json_from_file(self, filename: str,
                            encoding: str = 'utf-8') -> None:
        """Read JSON text from file to set internal data."""
        with open(file=filename, mode='r', encoding=encoding) as file:
            txt: str = file.read()
        self.parse_json(txt=txt)

    def read_xml_from_file(self, filename: str,
                           encoding: str = 'utf-8') -> None:
        """Read XML text from file to set internal data."""
        with open(file=filename, mode='r', encoding=encoding) as file:
            txt: str = file.read()
        self.parse_xml(txt=txt)


if __name__ == '__main__':  # pragma: no cover
    example = ExampleData()
    for i in range(3):
        print('')
    print(example.as_json_text())
    for i in range(3):
        print('')
    print(example.as_xml_text())
    AFILE = 'a.json'
    example.write_json_to_file(AFILE)
    example.read_json_from_file(AFILE)
    XFILE = 'b.xml'
    example.write_xml_to_file(filename=XFILE)
    example.read_xml_from_file(filename=XFILE)
    CFILE = 'c.json'
    example.write_json_to_file(CFILE)
    with open(file=AFILE, mode='r', encoding='utf-8') as afi:
        atxt = afi.read()
        with open(file=CFILE, mode='r', encoding='utf-8') as cfi:
            ctxt = cfi.read()
