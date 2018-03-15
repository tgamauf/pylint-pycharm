# Pylint-Pycharm

Pylint-Pycharm is a wrapper around Pylint that formats file paths in the Pylint output in a way that Pycharm understands. This allows you to go to the occurence of a finding dirctly by clicking on the provided link.

The tool accepts the directory of a virtual environment as parameter and requires the paths of one or more Python files as input. The Python files/modules and all additional command line parameters are handed over to Pylint.

## Setup
* Install Pylint via pip: `pip install --user pylint`
* Install Pylint-Pycharm:
    ```
    git clone https://github.com/perses76/pylint-pycharm.git
    cd pylint-pycharm
    python setup.py install
    ```
* Setup Pylint-Pycharm as an external tool in Pycharm:
    * `File\Settings`, then `Tools\External Tools`
    * Add tool by pressing `+`
    * Use the following settings:
        * Program: path to your installation of pylint-pycharm  
        * Arguments: `--virtualenv=$PyInterpreterDirectory$ $FilePath$`
        * Working directory: `$ProjectFileDir$`
        * Advanced Options\Output Filters: `$FILE_PATH$\:$LINE$\:$COLUMN$\:.*`

After setup you can execute Pylint-Pycharm through `Tools\External Tools\Pylint-Pycharm
    
