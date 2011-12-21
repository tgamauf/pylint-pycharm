"""
Tests for pylint-pycharm projects
"""
from unittest import TestCase
import unittest
import subprocess
import os

PROJECT_FOLDER = os.path.abspath(os.path.dirname(__file__))


class AcceptanceTest(TestCase):
    """
    Acceptance tests for pylint to pycharm parser
    """
    def test_success(self):
        """
        successful scenario
        """
        command = "python pylint_pycharm.py sample.py --reports=n"
        expected_result = "%s/sample.py:6:0: [C] More than one statement on a single line\n" % PROJECT_FOLDER
        pros = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        result = pros.stdout.read()
        self.assertEqual(result, expected_result)
        
class MainTest(TestCase):
    """
    tests for main.main function
    """
    def test_success(self):
        """
        successful scenario
        """
        import pylint_pycharm, StringIO
        io = StringIO.StringIO()
        args = ["pylint_pycharm.py", "sample.py", "--reports=n",  "--output-format=parseable"]
        expected_result = "%s/sample.py:6:0: [C] More than one statement on a single line\n" % PROJECT_FOLDER
        pylint_pycharm.main(args, io)
        result = io.getvalue()
        self.assertEqual(expected_result, result)

    def test_error(self):
        import pylint_pycharm, StringIO
        help_text = "This is help test"
        pylint_pycharm.HELP_TEXT = help_text
        original_parse_module_name = pylint_pycharm.parse_module_name
        pylint_pycharm.parse_module_name = MainTest.parse_module_name_mock
        io = StringIO.StringIO()
        pylint_pycharm.main([], io)
        result = io.getvalue()
        pylint_pycharm.parse_module_name = original_parse_module_name
        expected_result = "Error: exception\n"+help_text
        self.assertEqual(expected_result, result)


    @staticmethod
    def parse_module_name_mock(_):
        from pylint_pycharm import PylintPycharmException
        raise PylintPycharmException("exception")



class ParseModuleNameTests(TestCase):
    """
    tests for function main parse_module_name
    """

    def setUp(self):
        import pylint_pycharm
        self.parse_module_name = pylint_pycharm.parse_module_name
        self.PylintPycharmException = pylint_pycharm.PylintPycharmException

    def test_parse_module_name_success(self):
        """
        test if module_name is corrected extracted from list of arguments
        module_name has no dashes "-" in front and it is not first parameter
        """
        args = ["program_name", "--param1=test", "--param2=test2", "module_name"]
        module_name = self.parse_module_name(args)
        self.assertEqual("module_name", module_name)

    def test_parse_module_name_no_name(self):
        """
        module name is not provided
        """
        args = ["program_name", "--param1=test", "--param2=test2"]
        try:
            self.parse_module_name(args)
            self.fail("parse_module_name must not find any module name in this test")
        except self.PylintPycharmException:
            pass

    def test_parse_module_name_more_than_one_name(self):
        """
        module name is not provided
        """
        args = ["program_name", "--param1=test", "module_name1", "--param2=test2", "module_name2"]
        try:
            self.parse_module_name(args)
            self.fail("parse_module_name must not find any module name in this test")
        except self.PylintPycharmException:
            pass

class ParsePylintArgsTests(TestCase):
    """
    test of main.parse_pylint_args function
    """
    def setUp(self):
        import pylint_pycharm
        self.parse_pylint_args = pylint_pycharm.parse_pylint_args
        
    def test_success(self):
        """
        success scenario
        """
        args = ["program_name", "--param1=test", "module_name1", "--param2=test2"]
        result = self.parse_pylint_args(args)
        self.assertEquals(result, ["--param1=test", "--param2=test2"])

class FormatCommandForProcessTest(TestCase):
    """
    tests for main.parse_pylint_args function format_command_for_process
    """

    def setUp(self):
        import pylint_pycharm
        self.format_command_for_process = pylint_pycharm.format_command_for_process

    def test_success(self):
        module_name = "module_name"
        args = ["arg1", "arg2"]
        result = self.format_command_for_process(module_name, args)
        expected = "pylint module_name arg1 arg2"
        self.assertEqual(result, expected)

    def test_with_virtualenv(self):
        module_name = "module_name"
        args = ["arg1", "arg2"]
        virtual_path = "virtual_path"
        result = self.format_command_for_process(module_name, args, virtual_path)
        expected = ". virtual_path/bin/activate && pylint module_name arg1 arg2"
        self.assertEqual(result, expected)

class ParseOutputTest(TestCase):
    """
    tests for main.parse_output function
    """
    def test_success(self):
        """
        Success scenario
        """
        import pylint_pycharm
        root_path = "root_path"
        txt="filename:7: descr1\nsummary"
        expected_result="root_path/filename:7:0: descr1\nsummary"
        result = pylint_pycharm.parse_output(root_path, txt)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
  