#!/usr/bin/env python
# encoding: utf-8

# This layout for setup.py stolen shamelessly by zkbt
# from examples in dfm's and timothydmorton's github repos,
# with much gratitude to them for the help!

import os, sys, numpy, glob
from setuptools import setup, find_packages

# a little kludge to get the version number from __version__
exec(open('whatsup/version.py').read())

# Execute the setup command.
desc = open("README.rst").read()
setup(
    name="whatsup",
    version=__version__,
    author="Zach Berta-Thompson",
    author_email="zach.bertathompson@colorado.edu",
    packages=["whatsup"],
    #scripts=[g.strip('.py') for g in glob.glob('scripts/*.py')],
    url="http://github.com/zkbt/whatsup",
    license="MIT",
    description="What planets are up in the sky?",
    long_description=desc,
    package_data={"": ["README.rst", "LICENSE", ]},
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: MIT License",
        "Programming Language :: Python"],
    install_requires=['numpy', 'astropy', 'tqdm'])
