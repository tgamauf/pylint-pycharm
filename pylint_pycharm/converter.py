""" Pylint to Pycharm converter module. """

import sys
import os
import subprocess
import re


PYLINT_COMMAND = "pylint"
PYLINT_MESSAGE_PATTERN = r"^(?P<filename>[^:]*):(?P<line_number>\d+): (?P<description>.*)"
PYCHARM_MESSAGE_FORMAT = "%(full_path)s:%(line_number)s:0: %(description)s"
MAX_RECURSION = 10


class PylintPycharmError(Exception):
    """ Path not found in module<->path mappint. """

    def __init__(self, message):
        """
        Initialize error message.

        :param message: error message.
        :param errno: errno
        """

        self.message = message


def _get_key_path(cwd, path):
    """
    Get the path that is used as key in the file map.

    The given path can be an absolute path or a relative path
    Pylint returns relative paths if a relative path was given
    OR if the absolute path points to a subdirectory of the current
    working directory.

    :param cwd: current working directory that is used to determine key type.
    :param path: path that is the base for the mapping key.
    :returns the created key path.
    """

    if os.path.isabs(path) and path.startswith(cwd):
        key_path = path.split(cwd)[1].lstrip(os.sep)
    else:
        key_path = path

    return key_path


def _parse_directory(cwd, path):
    """
    Parse a directory and return a dictionary that maps the Pylint paths,
    which can be absolute or relative, to the absolute file paths required
    by Pycharm.

    :param cwd: current working directory that is used to determine key type.
    :param path: path that is the base for the mapping key.
    :returns mapping dictionary.
    """

    file_path_map = {}
    for root, _, files in os.walk(path):
        key_path = _get_key_path(cwd, root)
        abs_root_path = os.path.abspath(root)
        for file in files:
            key = os.path.join(key_path, file)
            file_path_map[key] = os.path.join(abs_root_path, file)

    return file_path_map


def _generate_file_map(inputs):
    """
    Create a dictionary that maps Pylint paths (absolute or relative) to
    the absolute paths that Pycharm understands.

    :param inputs: paths to input files or modules.
    :returns mapping dictionary.
    """

    cwd = os.getcwd()
    file_path_map = {}
    for path in inputs:
        # We need the absolute path as the file path in order for Pycharm
        # to recognize it.
        if os.path.isfile(path):
            key_path = _get_key_path(cwd, path)
            file_path_map[key_path] = os.path.abspath(path)
        else:
            directory_file_paths = _parse_directory(cwd, path)
            file_path_map.update(directory_file_paths)

    return file_path_map


def _prepare_pylint_args(args):
    """
    Filter and extend Pylint command line arguments.

    --output-format=parsable is required for us to parse the output.

    :param args: list of Pylint arguments.
    :returns extended list of Pylint arguments.
    """

    # Drop an already specified output format, as we need 'parseable'
    args = [a for a in args if not a.startswith("--output-format=")]

    args.append("--output-format=parseable")

    return args


def _format_pylint_command(modules, pylint_args, virtualenv_path=None):
    """
    Create Pylint command for execution.

    If a virtualenv is used, we activate it before Pylint is called and
    deactivate it afterwards.

    :param modules: paths to files and packages that should be linted.
    :param pylint_args: list of Pylint arguments.
    :param virtualenv_path: path to virtualenv that must be used.
    :returns: command for execution on command line.
    """

    args_str = " ".join(pylint_args)
    modules_str = " ".join(modules)
    command = "%s %s %s" % (PYLINT_COMMAND, modules_str, args_str)

    if virtualenv_path:
        activate_venv_command = os.path.join(virtualenv_path, "activate")
        deactivate_venv_command = "deactivate"

        # There is no source command in windows, "activate" is simply a script
        command = "%s%s && %s && %s" % ('. ' if os.name != 'nt' else '',
                                        activate_venv_command,
                                        command,
                                        deactivate_venv_command)

    return command


def _run_pylint(command):
    """
    Run Pylint on the command line.

    :param command: command for execution on command line.
    :returns tuple of command exit code and Pylint output.
    :raises PylintPycharmError if command execution failed.
    """

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    except OSError:
        raise PylintPycharmError("Command '%s' failed" % command)

    pylint_output = process.stdout.read().decode('utf-8')

    exit_code = process.wait()
    if exit_code == 127:
        raise PylintPycharmError("Command '%s' not found" % command)

    return exit_code, pylint_output


def _parse_output(file_path_map, txt):
    """
    Parse the Pylint output text and convert it to a Pycharm compatible format.

    :param file_path_map: mapping of Pylint paths to Pycharm paths.
    :param txt: Pylint output text.
    :returns Pycharm compatible text.
    """

    result = []
    lines = txt.split("\n")
    for line in lines:
        match = re.match(PYLINT_MESSAGE_PATTERN, line)
        if match:
            filename = match.group('filename')

            try:
                full_file_path = file_path_map[filename]
            except KeyError:
                raise PylintPycharmError("No root path found for module %s" % filename)

            data = {"full_path": full_file_path,
                    "line_number": match.group("line_number"),
                    "description": match.group("description")}
            result.append(PYCHARM_MESSAGE_FORMAT % data)
        else:
            result.append(line)

    return "\n".join(result)


def convert(inputs, pylint_args, virtualenv_path):
    """
    Convert Pylint messages to PyCharm messages.

    :param inputs: input paths for parsing.
    :param pylint_args: arguments that are passed to Pylint.
    :param virtualenv_path: path to virtual environment.
    :raises PylintPycharmError: on execution error.
    """

    pylint_args = _prepare_pylint_args(pylint_args)
    command = _format_pylint_command(inputs, pylint_args, virtualenv_path)
    pylint_exit_code, pylint_output = _run_pylint(command)

    file_path_map = _generate_file_map(inputs)
    output_text = _parse_output(file_path_map, pylint_output)
    sys.stdout.write(output_text)

    return pylint_exit_code
