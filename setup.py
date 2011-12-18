from distutils.core import setup
setup(
    name = "pylint_pycharm",
    packages = ["pylint_pycharm"],
    version = "0.9",
    description = "Pylint to Pycharm message converter",
    author = "Wadim Ovcharenko",
    author_email = "wadim@veles-soft.com",
    keywords = ["pylint", "pycharm"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        ],
    long_description = """\
Pylint to Pycharm message converter
-------------------------------------

Convert messages from pylint report to pycharm format

Pylint format (with --output-format=parseable)
sample.py:6: [C] More than one statement on a single line

pylint_pychar format:
/home/vadim/Projects/pylint-pycharm/sample.py:6:0: [C] More than one statement on a single line
"""
)