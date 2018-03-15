""" Pylint to Pycharm message converter script entry point. """

import argparse
import sys

from .converter import convert, PylintPycharmError


def main():
    """ Pylint to Pycharm script entry point. """

    parser = argparse.ArgumentParser(
        description="Pylint to Pycharm message converter. "
                    "Additional arguments starting with '--' are forwarded to Pylint."
    )
    parser.add_argument("-v", "--virtualenv", help="path to virtual environment")
    parser.add_argument("inputs", nargs='+', help='input files and modules to parse')
    parser.add_argument("pylint_args", default=[], nargs=argparse.REMAINDER)
    args = parser.parse_args(sys.argv[1:])

    try:
        exit_code = convert(args.inputs, args.pylint_args, args.virtualenv)
        sys.exit(exit_code)
    except PylintPycharmError as error:
        sys.stderr.write("Pylint execution failed: %s" % error.message)
        sys.exit(1)
