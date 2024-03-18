import copy
import json
import logging
import os
import uuid
from slugify import slugify
import nbformat as nb
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.pyextractor import PyExtractor
from jupyterlab_vre.services.extractor.rextractor import RExtractor


# TODO: we might have to do something similar here where we have to determine the kernel and based on that get the extractor

class NotebookExtractorHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        msg_json = dict(title='Operation not supported.')
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
        logging.getLogger(__name__).debug('NotebookExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        print('----------------------------------------------')
        print('NotebookExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        print('----------------------------------------------')
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        kernel = payload['kernel']
        if kernel == "IRkernel":
            extractor = RExtractor(notebook)
        else:
            extractor = PyExtractor(notebook)
        source = ''
        params = set()
        confs = set()
        ins = dict()
        outs = extractor.infer_cell_outputs(notebook.cells[len(notebook.cells) - 1].source)
        title = ''
        for cell_source in extractor.sources:
            p = extractor.extract_cell_params(cell_source)
            params.update(p)
            c = extractor.extract_cell_conf_ref(source)
            confs.update(c)
            source += cell_source + '\n'

            if not title:
                title = cell_source.partition('\n')[0].strip()
                title = 'notebook-' + slugify(title)
            else:
                title = 'Untitled'
                if 'JUPYTERHUB_USER' in os.environ:
                    title += '-' + slugify(os.environ['JUPYTERHUB_USER'])
        dependencies = extractor.infer_cell_dependencies(source, confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=slugify(title.lower()),
            original_source=source,
            inputs=ins,
            outputs=outs,
            params=list(params),
            confs=list(confs),
            dependencies=list(dependencies),
            container_source=''
        )
        cell.integrate_configuration()
        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            set(ins),
            set(outs),
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
        logging.getLogger(__name__).debug('NotebookExtractorHandler. cell: ' + str(cell.toJSON()))
        self.write(cell.toJSON())
        self.flush()
