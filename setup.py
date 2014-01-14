# -*- coding: utf-8 -*-
"""
Etch
~~~~

Etch is a maximally minimal pure-Python templating language.

"""
from setuptools import setup

from etch import (__version__,
                  __author__,
                  __contact__,
                  __url__,
                  __license__)

setup(
    name='etch',
    version=__version__,
    author=__author__,
    author_email=__contact__,
    license=__license__,
    url=__url__,
    description='Featherweight templating for Python',
    long_description=__doc__,
    py_modules=('etch',),
    scripts=('etch.py',),
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup'],
)
