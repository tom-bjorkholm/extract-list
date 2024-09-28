#! /usr/local/bin/python3
"""Setup file specifying build of apo_tools.whl with APO tools library."""

from setuptools import setup

setup(
  name='extract-list',
  version='0.1',
  description='Extract a list from JSON or XML, save to excel, csv, etc.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12.6',
  packages=['extract_list'],
  package_dir={'extract_list': 'src/extract_list'},
  install_requires=[
    'excel-list-transform >= 0.6',
    'xmltodict >= 0.13.0',
    'pip >= 24.2',
    'setuptools >= 75.1.0',
    'build >= 1.2.2',
    'wheel>=0.44.0'
  ]
)
