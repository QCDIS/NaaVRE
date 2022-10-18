import json
import os
import uuid
from unittest import TestCase
import nbformat as nb
import logging

from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.extractor import Extractor
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'

print(base_path)
class TestExtractor(TestCase):

    def test_all_infer_cell_inputs(self):
        self.infer_cell_inputs(os.path.join(base_path, 'notebooks/MULTIPLY_framework_cells.json'))
        self.infer_cell_inputs(os.path.join(base_path, 'notebooks/laserfarm_cells.json'))
        self.infer_cell_inputs(os.path.join(base_path, 'notebooks/vol2bird_cells.json'))
        try:
            self.infer_cell_inputs(os.path.join(base_path, 'notebooks/MULTIPLY_framework_2.json'))
        except SyntaxError as e:
            logger.warning(str(e))

    def infer_cell_inputs(self, payload_path):
        with open(payload_path, 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

        source = notebook.cells[cell_index].source
        title = source.partition('\n')[0]
        title = title.replace('#', '').replace(
            '_', '-').replace('(', '-').replace(')', '-').strip() if title[0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + os.environ['JUPYTERHUB_USER']
            title.replace('_', '-').replace('(', '-').replace(')', '-').strip()

        ins = []
        outs = []
        params = []
        confs = []
        dependencies = []
        # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infere_cell_inputs(source)'
        if notebook.cells[cell_index].cell_type == 'code':
            ins = set(extractor.infere_cell_inputs(source))
            outs = set(extractor.infere_cell_outputs(source))

            confs = extractor.extract_cell_conf_ref(source)
            dependencies = extractor.infer_cell_dependencies(source, confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=title.lower().replace(' ', '-'),
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
            params = list(extractor.extract_cell_params(cell.original_source))
            cell.params = params

        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            ins,
            outs,
            params,
            dependencies
        )

        chart = {
            'offset': {
                'x': 0,
                'y': 0,
            },
            'scale': 1,
            'nodes': {node_id: node},
            'links': {},
            'selected': {},
            'hovered': {},
        }

        cell.chart_obj = chart

        print(cell.toJSON())
