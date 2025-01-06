#! /usr/local/bin/python3
"""Setup file specifying build of apo_tools.whl with APO tools library."""

from setuptools import setup

setup(
  name='extract-list',
  version='0.2',
  description='Extract a list from JSON or XML, save to excel, csv, etc.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12.6',
  packages=['extract_list'],
  package_dir={'extract_list': 'src/extract_list'},
  package_data={'extract_list': ['src/py.typed']},
  install_requires=[
    'excel-list-transform >= 0.7.1',
    'xmltodict >= 0.13.0',
    'types-xmltodict >= 0.13.0.3',
    'pip >= 24.2',
    'setuptools >= 75.6.0',
    'build >= 1.2.2',
    'wheel>=0.45.1'
  ]
)
