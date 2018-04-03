""" Tests for converter. """

from unittest import TestCase, main
try:
    from unittest.mock import patch
except ImportError:
	from mock.mock import patch
import os.path

import pylint_pycharm.converter as converter


class TestPylintPycharm(TestCase):

    @patch("os.path.isabs")
    def test_get_key_path(self, mock_isabs):
        mock_isabs.return_value = False
        key_path = converter._get_key_path("a", "a/b")
        self.assertEqual(key_path, "a/b")

        mock_isabs.return_value = True
        key_path = converter._get_key_path("/a", "/a/b")
        self.assertEqual(key_path, "b")

        mock_isabs.return_value = True
        key_path = converter._get_key_path("a", "/c/d")
        self.assertEqual(key_path, "/c/d")

    @patch("os.walk")
    @patch("os.path.abspath")
    @patch("pylint_pycharm.converter._get_key_path")
    def test_parse_directory(self, mock_get_key_path, mock_abspath, mock_walk):
        mock_walk.return_value = [("b", [], [])]
        file_path_map = converter._parse_directory("cwd", "b")
        self.assertDictEqual(file_path_map, {})
        mock_get_key_path.assert_called_once_with("cwd", "b")

        mock_walk.return_value = [("b", ["c"], ["file_1.py", "file_2.py"])]
        mock_abspath.return_value = os.path.join("a", "b")
        mock_get_key_path.return_value = "key_path"
        file_path_map = converter._parse_directory("cwd", "b")
        self.assertDictEqual(
            file_path_map,
            {os.path.join("key_path", "file_1.py"): os.path.join("a", "b", "file_1.py"),
             os.path.join("key_path", "file_2.py"): os.path.join("a", "b", "file_2.py")}
        )

    @patch("os.path.isfile")
    @patch("pylint_pycharm.converter._get_key_path")
    @patch("pylint_pycharm.converter._parse_directory")
    def test_generate_file_map(self,
                               mock_parse_directory,
                               mock_get_key_path,
                               mock_isfile):
        file_path_map = converter._generate_file_map([])
        self.assertDictEqual(file_path_map, {})

        mock_isfile.side_effect = [True, False]
        mock_get_key_path.return_value = "key_path"
        mock_parse_directory.return_value = {"dir_key_path": "dir"}
        file_path_map = converter._generate_file_map(["file.py", "dir"])
        self.assertDictEqual(
            file_path_map,
            {"key_path": os.path.join(os.getcwd(), "file.py"),
             "dir_key_path": "dir"}
        )

    def test_prepare_pylint_args(self):
        args = converter._prepare_pylint_args(["--test=a", "--output-format=json"])
        self.assertListEqual(args, ["--test=a", "--output-format=parseable"])

        args = converter._prepare_pylint_args([])
        self.assertListEqual(args, ["--output-format=parseable"])

    def test_format_pylint_command(self):
        converter.PYLINT_COMMAND = "pylint"
        test_modules = ["/a/file.py", "c/d"]
        test_pylint_args = ["--test=a", "-t=b"]
        test_virtualenv_path = "venv/bin"

        cmd = converter._format_pylint_command(test_modules, test_pylint_args)
        self.assertEqual(cmd, "pylint /a/file.py c/d --test=a -t=b")

        cmd = converter._format_pylint_command(test_modules,
                                               test_pylint_args,
                                               test_virtualenv_path)
        self.assertEqual(cmd,
                         ". %s && pylint /a/file.py c/d --test=a -t=b && deactivate"
                         % os.path.join("venv", "bin", "activate"))

    @patch("subprocess.Popen")
    def test_run_pylint(self, mock_popen):
        import subprocess
        mock_popen.return_value.stdout.read.return_value = b"test\ntext"
        mock_popen.return_value.wait.return_value = 1
        exit_code, output = converter._run_pylint("command")
        self.assertEqual(exit_code, 1)
        mock_popen.assert_called_once_with("command",
                                           shell=True,
                                           stdout=subprocess.PIPE)
        self.assertEqual(output, "test\ntext")

        mock_popen.return_value.wait.return_value = 127
        with self.assertRaises(converter.PylintPycharmError):
            converter._run_pylint("command")

        mock_popen.side_effect = OSError()
        with self.assertRaises(converter.PylintPycharmError):
            converter._run_pylint("command")

    def test_parse_output(self):
        test_file_path_map = {"a": "/c/a", "/b": "/b"}
        test_text = "a:100: some text\nMore text\n/b:3: t"
        output = converter._parse_output(test_file_path_map, test_text)
        self.assertEqual(output, "/c/a:100:0: some text\nMore text\n/b:3:0: t")

        test_file_path_map = {}
        test_text = "INVALID:100: some text"
        with self.assertRaises(converter.PylintPycharmError):
            converter._parse_output(test_file_path_map, test_text)

    @patch("pylint_pycharm.converter._prepare_pylint_args")
    @patch("pylint_pycharm.converter._format_pylint_command")
    @patch("pylint_pycharm.converter._run_pylint")
    @patch("pylint_pycharm.converter._generate_file_map")
    @patch("pylint_pycharm.converter._parse_output")
    def test_convert(self,
                     mock_parse_output,
                     mock_generate_file_map,
                     mock_run_pylint,
                     mock_format_pylint_command,
                     mock_prepare_pylint_args):
        mock_run_pylint.return_value = (22, "text")
        mock_parse_output.return_value = "test_output"
        exit_code = converter.convert("inputs", "pylint_args", "virtualenv_path")
        self.assertEqual(exit_code, 22)
        mock_prepare_pylint_args.assert_called_once_with("pylint_args")
        mock_format_pylint_command.assert_called_once_with(
            "inputs",
            mock_prepare_pylint_args.return_value,
            "virtualenv_path"
        )
        mock_run_pylint.assert_called_once_with(
            mock_format_pylint_command.return_value)
        mock_generate_file_map.assert_called_once_with("inputs")
        mock_parse_output.assert_called_once_with(
            mock_generate_file_map.return_value,
            "text"
        )


if __name__ == "__main__":
    main()
