from setuptools import setup
import sys, os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(name='typeinfo',
      version=version,
      description='A library to add optional type information to python objects.',
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='TypeInfo Developers',
      author_email='b.leskes@gmail.com',
      url='',
      license='apache',
      py_modules=['typeinfo'],
      package_dir={ "": "src"},
      zip_safe=False,
      install_requires=[
      ])