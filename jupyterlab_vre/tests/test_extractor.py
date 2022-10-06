import json
import os
from unittest import TestCase
import nbformat as nb

from jupyterlab_vre.services.extractor.extractor import Extractor


class TestExtractor(TestCase):


    def test_vol2bird(self):
        with open('resources/vol2bird_cells.json', 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)


    def test_MULTIPLY(self):
        with open('resources/MULTIPLY_framework_cells.json', 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)



    def test_infere_cell_inputs(self):
        with open('resources/MULTIPLY_framework_cells.json', 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)
        if notebook.cells[cell_index].cell_type == 'code':
            source = notebook.cells[cell_index].source
            title = source.partition('\n')[0]
            title = title.replace('#', '').replace(
                '_', '-').replace('(', '-').replace(')', '-').strip() if title[0] == "#" else "Untitled"

            if 'JUPYTERHUB_USER' in os.environ:
                title += '-' + os.environ['JUPYTERHUB_USER']
                title.replace('_', '-').replace('(', '-').replace(')', '-').strip()
            try:
                ins = set(extractor.infere_cell_inputs(source))
                outs = set(extractor.infere_cell_outputs(source))
            except Exception as e:
                print(e)
            params = []
            confs = extractor.extract_cell_conf_ref(source)
            dependencies = extractor.infere_cell_dependencies(source, confs)
