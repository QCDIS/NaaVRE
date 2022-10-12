import copy
import json
import logging
import os
import uuid

import nbformat as nb
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.extractor import Extractor


class NotebookExtractorHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        msg_json = dict(title='Operation not supported.')
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
        logging.getLogger(__name__).debug('NotebookExtractorHandler. payload: ' + str(payload))
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)
        source = ''
        params = set()
        confs = set()
        ins = set()
        outs = set(extractor.infere_cell_outputs(notebook.cells[len(notebook.cells) - 1].source))
        title = ''
        for cell_source in extractor.sources:
            p = extractor.extract_cell_params(cell_source)
            params.update(p)
            c = extractor.extract_cell_conf_ref(source)
            confs.update(c)
            source += cell_source + '\n'

            if not title:
                title = cell_source.partition('\n')[0]
                title = 'notebook-'+title.replace('#', '').replace('_', '-').replace('(', '-').replace(')', '-').strip() if title[0] == '#' \
                    else 'Untitled'
                if 'JUPYTERHUB_USER' in os.environ:
                    title += '-' + os.environ['JUPYTERHUB_USER']

        dependencies = extractor.infer_cell_dependencies(source, confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=title.lower().replace(' ', '-'),
            original_source=source,
            inputs=list(ins),
            outputs=list(outs),
            params=list(params),
            confs=list(confs),
            dependencies=list(dependencies),
            container_source=''
        )
        cell.integrate_configuration()
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
        logging.getLogger(__name__).debug('NotebookExtractorHandler. cell: ' + str(cell.toJSON()))
        self.write(cell.toJSON())
        self.flush()

