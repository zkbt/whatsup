#!/usr/bin/env python
# encoding: utf-8

# This layout for setup.py stolen shamelessly by zkbt
# from examples in dfm's and timothydmorton's github repos,
# with much gratitude to them for the help!


import os, sys, numpy, glob

# import setup functions
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# publish the library to PyPI.
if "publish" in sys.argv[1:]:
    os.system("python setup.py sdist upload")
    sys.exit()

# hackishly inject a constant into builtins to enable importing of the
# package before the library is built.
if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
builtins.__WHATSUP__ = True
import whatsup

# Execute the setup command.
desc = open("README.rst").read()
setup(
    name="whatsup",
    version=whatsup.__version__,
    author="Zach Berta-Thompson",
    author_email="zach.bertathompson@colorado.edu",
    packages=[
        "whatsup"
    ],
    scripts=[g.strip('.py') for g in glob.glob('scripts/*.py')],
    url="http://github.com/zkbt/whatsup",
    license="MIT",
    description="What planets are up in the sky?",
    long_description=desc,
    package_data={"": ["README.rst", "LICENSE", ]},
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: MIT License",
        "Programming Language :: Python",
    ],
)
