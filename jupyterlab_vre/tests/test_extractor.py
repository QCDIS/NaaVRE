import ast
import glob
import json
import logging
import os
from unittest import TestCase
import pytest

import nbformat as nb

from jupyterlab_vre.services.extractor.extract_cell import extract_cell


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'


def extract_cell_from_path(payload_path):
    # Check if file exists
    if os.path.exists(payload_path):
        with open(payload_path, 'r') as file:
            payload = json.load(file)

        cell = extract_cell(
            nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT),
            payload['cell_index'],
            payload['kernel'],
            )

        return cell.toJSON()
    return None


class PyAssertNoConfInAssign(ast.NodeVisitor):

    def __init__(self, msg):
        self.msg = msg

    def visit_Assign(self, node):
        # visit the 'value' side of assignments (*<node.targets> = node.value)
        self.generic_visit(node.value)

    def visit_Name(self, node):
        # return if a variable named conf_* is found
        assert not node.id.startswith('conf_'), self.msg


class TestExtractor(TestCase):
    # Reference parameter values for `test_param_values_*.json`
    param_values_ref = {
        'param_float': 1.1,
        'param_int': 1,
        'param_list': [1, 2, 3],
        'param_string': 'param_string value',
        'param_string_with_comment': 'param_string value'
    }

    @pytest.mark.timeout(60)
    def test_extract_cell(self):
        notebooks_json_path = os.path.join(base_path, 'notebooks')
        notebooks_files = glob.glob(
            os.path.join(notebooks_json_path, "*.json")
        )
        for notebook_file in notebooks_files:
            if 'test_param_values_R.json' not in notebook_file:
                continue
            cell = extract_cell_from_path(notebook_file)
            logging.getLogger().debug(notebook_file)
            print(notebook_file)
            if cell:
                cell = json.loads(cell)
                for conf_name, conf_value in cell['confs'].items():
                    assignment_symbol = '='
                    if '<-' in conf_value:
                        assignment_symbol = '<-'
                    msg = ('conf_ values should not contain conf_ prefix '
                           'in assignment')
                    if 'python' in cell['kernel'].lower():
                        PyAssertNoConfInAssign(msg).visit(ast.parse(conf_value))
                    else:
                        self.assertFalse(
                            'conf_' in conf_value.split(assignment_symbol)[1],
                            msg)
                for param_name in cell['params']:
                    self.assertTrue(param_name in cell['param_values'])

                # For notebook_file test_param_values_*.json, extracted params
                # should match with self.param_values_ref
                if (os.path.basename(notebook_file) in
                        ['test_param_values_Python.json',
                         'test_param_values_R.json',
                         ]):
                    for param_name in cell['params']:
                        if not cell['param_values'][param_name] == self.param_values_ref[param_name]:
                            print(cell['param_values'][param_name])
                            print(self.param_values_ref[param_name])
                        self.assertTrue(
                            cell['param_values'][param_name] ==
                            self.param_values_ref[param_name]
                        )
