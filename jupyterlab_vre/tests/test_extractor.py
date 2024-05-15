import glob
import json
import logging
import os
import uuid
from unittest import TestCase
import pytest

import nbformat as nb
from slugify import slugify

from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.pyextractor import PyExtractor
from jupyterlab_vre.services.extractor.rextractor import RExtractor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'


def create_cell(payload_path=None):
    with open(payload_path, 'r') as file:
        payload = json.load(file)

    cell_index = payload['cell_index']
    notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
    source = notebook.cells[cell_index].source
    if payload['kernel'] == "IRkernel":
        extractor = RExtractor(notebook, source)
    else:
        extractor = PyExtractor(notebook, source)

    title = source.partition('\n')[0]
    title = slugify(title) if title and title[
        0] == "#" else "Untitled"

    if 'JUPYTERHUB_USER' in os.environ:
        title += '-' + slugify(os.environ['JUPYTERHUB_USER'])

    ins = {}
    outs = {}
    params = {}
    confs = []
    dependencies = []

    # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infere_cell_inputs(
    # source)'
    if notebook.cells[cell_index].cell_type == 'code':
        ins = extractor.infer_cell_inputs()
        outs = extractor.infer_cell_outputs()

        confs = extractor.extract_cell_conf_ref()
        dependencies = extractor.infer_cell_dependencies(confs)

    node_id = str(uuid.uuid4())[:7]
    cell = Cell(
        node_id=node_id,
        title=title,
        task_name=slugify(title.lower()),
        original_source=source,
        inputs=ins,
        outputs=outs,
        params=params,
        confs=confs,
        dependencies=dependencies,
        container_source=""
    )
    if notebook.cells[cell_index].cell_type == 'code':
        cell.integrate_configuration()
        params = extractor.extract_cell_params(cell.original_source)
        cell.add_params(params)
        cell.add_param_values(params)

    return cell


def extract_cell(payload_path):
    # Check if file exists
    if os.path.exists(payload_path):
        cell = create_cell(payload_path)

        node = ConverterReactFlowChart.get_node(
            cell.node_id,
            cell.title,
            cell.inputs,
            cell.outputs,
            cell.params,
        )

        chart = {
            'offset': {
                'x': 0,
                'y': 0,
            },
            'scale': 1,
            'nodes': {cell.node_id: node},
            'links': {},
            'selected': {},
            'hovered': {},
        }

        cell.chart_obj = chart
        return cell.toJSON()
    return None


class TestExtractor(TestCase):

    # Reference parameter values for `test_param_values_*.json`
    param_values_ref = {
        'param_float': '1.1',
        'param_int': '1',
        'param_list': '[1, 2, 3]',
        'param_string': 'param_string value',
        'param_string_with_comment': 'param_string value',
        }

    @pytest.mark.timeout(60)
    def test_extract_cell(self):
        notebooks_json_path = os.path.join(base_path, 'notebooks')
        notebooks_files = glob.glob(
            os.path.join(notebooks_json_path, "*.json")
            )
        for notebook_file in notebooks_files:
            cell = extract_cell(notebook_file)
            print(notebook_file)
            if cell:
                cell = json.loads(cell)
                for conf_name in (cell['confs']):
                    assignment_symbol = '='
                    if '<-' in cell['confs'][conf_name]:
                        assignment_symbol = '<-'
                    self.assertFalse('conf_' in cell['confs'][conf_name].split(assignment_symbol)[1],
                                     'conf_ values should not contain conf_ prefix in '
                                     'assignment')
                # All params should have matching values
                for param_name in cell['params']:
                    self.assertTrue(param_name in cell['param_values'])

                # For notebook_file test_param_values_*.json, extracted params
                # should match with self.param_values_ref
                if (os.path.basename(notebook_file) in
                        ['test_param_values_Python.json',
                         'test_param_values_R.json',
                         ]):
                    for param_name in cell['params']:
                        self.assertTrue(
                            cell['param_values'][param_name] ==
                            self.param_values_ref[param_name]
                            )
