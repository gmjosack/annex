#!/usr/bin/env python

from distutils.core import setup

kwargs = {
    "name": "annex",
    "version": "0.1",
    "py_modules": ["annex"],
    "scripts": [],
    "description": "A Simple Plugin System for Python",
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
