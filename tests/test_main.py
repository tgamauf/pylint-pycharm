""" Tests for __main__. """

from unittest import TestCase, main
try:
    from unittest.mock import patch
except ImportError:
    from mock.mock import patch

import pylint_pycharm.__main__
from pylint_pycharm.converter import PylintPycharmError


class TestMain(TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    @patch('pylint_pycharm.__main__.convert')
    @patch('sys.exit')
    def test_main(self, mock_exit, mock_convert, mock_parse_args):
        mock_parse_args.return_value.inputs = 'inputs'
        mock_parse_args.return_value.pylint_args = 'pylint_args'
        mock_parse_args.return_value.virtualenv = 'virtualenv'
        mock_convert.return_value = 22
        pylint_pycharm.__main__.main()
        mock_convert.assert_called_once_with('inputs', 'pylint_args', 'virtualenv')
        mock_exit.assert_called_once_with(22)

        mock_exit.reset_mock()
        mock_convert.side_effect = PylintPycharmError(message='test')
        pylint_pycharm.__main__.main()
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    main()
