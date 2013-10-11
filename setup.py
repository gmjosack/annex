#!/usr/bin/env python

from distutils.core import setup

execfile('annex/version.py')

kwargs = {
    "name": "annex",
    "version": str(__version__),
    "packages": ["annex"],
    "scripts": [],
    "description": "A Simple Plugin System for Python",
    "long_description": open("README").read(),
    "author": "Gary M. Josack",
    "maintainer": "Gary M. Josack",
    "author_email": "gary@byoteki.com",
    "maintainer_email": "gary@byoteki.com",
    "license": "MIT",
    "url": "https://github.com/gmjosack/annex",
    "download_url": "https://github.com/gmjosack/annex/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
