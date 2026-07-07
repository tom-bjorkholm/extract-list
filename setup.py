#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='extract-list',
  version='0.6',
  description='Extract a list from JSON or XML, save to excel, csv, etc.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.13',
  packages=['extract_list'],
  package_dir={'extract_list': 'src/extract_list'},
  package_data={'extract_list': ['src/py.typed']},
  install_requires=[
    'argcomplete >= 3.7.0',
    'config-as-json >= 1.4',
    'tableio >= 1.1',
    'tableio-cfg-json >= 0.8',
    'versionreporter >= 0.4',
    'xmltodict >= 1.0.4',
    'types-xmltodict >= 1.0.1.20260518'
  ]
)
