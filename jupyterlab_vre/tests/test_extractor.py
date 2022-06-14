import json
from unittest import TestCase
import nbformat as nb

from jupyterlab_vre.extractor.extractor import Extractor


class TestExtractor(TestCase):


    def test(self):
        with open('resources/vol2bird_cells.json', 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

