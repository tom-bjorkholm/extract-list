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
    'config-as-json >= 1.0',
    'tableio >= 0.9',
    'tableio-cfg-json >= 0.2',
    'versionreporter >= 0.2',
    'xmltodict >= 1.0.4',
    'types-xmltodict >= 1.0.1.20260408',
    'pip >= 26.1.1',
    'setuptools >= 82.0.1',
    'build >= 1.5.0',
    'wheel>=0.47.0'
  ]
)
