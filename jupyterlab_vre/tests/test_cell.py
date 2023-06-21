import json
import os
import re
from pathlib import Path
from unittest import TestCase

from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.database.cell import Cell

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'



class TestCell(TestCase):

    cells_json_path = None

    @classmethod
    def setUpClass(self):
        if os.path.exists('resources'):
            self.base_path = 'resources'
        elif os.path.exists('jupyterlab_vre/tests/resources/'):
            self.base_path = 'jupyterlab_vre/tests/resources/'
        self.cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
        self.cells_json_path = os.path.join(base_path, 'cells')
        self.cells_files = os.listdir(self.cells_json_path)

    def test_clean_code(self):
        for cell_file in self.cells_files:
            cell_path = os.path.join(self.cells_json_path, cell_file)
            with open(cell_path, 'r') as file:
                cell = json.load(file)
            file.close()
            test_cell = Cell(cell['title'], cell['task_name'], cell['original_source'], cell['inputs'],
                             cell['outputs'],
                             cell['params'], cell['confs'], cell['dependencies'], cell['container_source'],
                             cell['chart_obj'], cell['node_id'], cell['kernel'])
            test_cell.types = cell['types']
            test_cell.base_image = cell['base_image']
            Catalog.editor_buffer = test_cell
            test_cell.clean_code()
            for line in cell['original_source'].splitlines():
                if line.startswith('param_'):
                    # clean param name
                    pattern = r"\b(param_\w+)\b"
                    param_name = re.findall(pattern, line)[0]
                    if param_name not in test_cell.params:
                        self.assertIn(line, test_cell.original_source)