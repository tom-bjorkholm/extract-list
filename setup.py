#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='extract-list',
  version='0.2.15',
  description='Extract a list from JSON or XML, save to excel, csv, etc.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.13',
  packages=['extract_list'],
  package_dir={'extract_list': 'src/extract_list'},
  package_data={'extract_list': ['src/py.typed']},
  install_requires=[
    'argcomplete >= 3.6.3',
    'excel-list-transform >= 0.8.5',
    'xmltodict >= 1.0.2',
    'types-xmltodict >= 1.0.1.20250920',
    'pip >= 25.3',
    'setuptools >= 80.9.0',
    'build >= 1.3.0',
    'wheel>=0.45.1'
  ]
)
