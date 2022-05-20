import copy
import json
import uuid
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.extractor import Extractor

import nbformat as nb
from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.storage.faircell import Cell
from notebook.base.handlers import APIHandler
from tornado import web


class ExtractorHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

        source = notebook.cells[cell_index].source

        title = source.partition('\n')[0]
        title = title.replace('#', '').replace(
            '_', '-').replace('(', '-').replace(')', '-').strip() if title[0] == "#" else "Untitled"

        ins = set(extractor.infere_cell_inputs(source))
        outs = set(extractor.infere_cell_outputs(source))
        params = []
        confs = extractor.extract_cell_conf_ref(source)
        dependencies = extractor.infere_cell_dependencies(source, confs)

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

        Catalog.editor_buffer = copy.deepcopy(cell)

        self.write(cell.toJSON())

        self.flush()


class TypesHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        port = payload['port']
        p_type = payload['type']
        cell = Catalog.editor_buffer
        cell.types[port] = p_type


class BaseImageHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        base_image = payload['image']
        cell = Catalog.editor_buffer
        print(payload)
