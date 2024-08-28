import copy
import os
import json
import hashlib

from slugify import slugify

from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.extractor import DummyExtractor
from jupyterlab_vre.services.extractor.pyextractor import PyExtractor
from jupyterlab_vre.services.extractor.rextractor import RExtractor
from jupyterlab_vre.services.extractor.pyheaderextractor import PyHeaderExtractor
from jupyterlab_vre.services.extractor.rheaderextractor import RHeaderExtractor


def extract_cell_by_index(notebook, cell_index):
    new_nb = copy.deepcopy(notebook)
    if cell_index < len(notebook.cells):
        new_nb.cells = [notebook.cells[cell_index]]
        return new_nb


def set_notebook_kernel(notebook, kernel):
    new_nb = copy.deepcopy(notebook)
    # Replace kernel name in the notebook metadata
    new_nb.metadata.kernelspec.name = kernel
    new_nb.metadata.kernelspec.display_name = kernel
    new_nb.metadata.kernelspec.language = kernel
    return new_nb


def extract_cell(notebook, cell_index, kernel):

    source = notebook.cells[cell_index].source

    if notebook.cells[cell_index].cell_type != 'code':
        # dummy extractor for non-code cells (e.g. markdown)
        extractor = DummyExtractor(notebook, source)
    else:
        # extractor based on the cell header
        if 'python' in kernel.lower():
            extractor = PyHeaderExtractor(notebook, source)
        elif 'r' in kernel.lower():
            extractor = RHeaderExtractor(notebook, source)
        # Extractor based on code analysis. Used if the cell has no header,
        # or if some values are not specified in the header
        if not extractor.is_complete():
            if kernel == "IRkernel":
                code_extractor = RExtractor(notebook, source)
            else:
                code_extractor = PyExtractor(notebook, source)
            extractor.add_missing_values(code_extractor)

    extracted_nb = extract_cell_by_index(notebook, cell_index)
    if kernel == "IRkernel":
        extracted_nb = set_notebook_kernel(extracted_nb, 'R')
    else:
        extracted_nb = set_notebook_kernel(extracted_nb, 'python3')

    # initialize variables
    title = source.partition('\n')[0].strip()
    title = slugify(title) if title and title[0] == "#" else "Untitled"

    if 'JUPYTERHUB_USER' in os.environ:
        title += '-' + slugify(os.environ['JUPYTERHUB_USER'])

    # If any of these change, we create a new cell in the catalog.
    # This matches the cell properties saved in workflows.
    cell_identity_dict = {
        'title': title,
        'params': extractor.params,
        'secrets': extractor.secrets,
        'inputs': extractor.ins,
        'outputs': extractor.outs,
        }
    cell_identity_str = json.dumps(cell_identity_dict, sort_keys=True)
    node_id = hashlib.sha1(cell_identity_str.encode()).hexdigest()[:7]

    cell = Cell(
        node_id=node_id,
        title=title,
        task_name=slugify(title.lower()),
        original_source=source,
        inputs=extractor.ins,
        outputs=extractor.outs,
        params={},
        secrets={},
        confs=extractor.confs,
        dependencies=extractor.dependencies,
        container_source="",
        kernel=kernel,
        notebook_dict=extracted_nb.dict()
        )
    cell.integrate_configuration()
    params = extractor.extract_cell_params(cell.original_source)
    extractor.params = params
    cell.add_params(params)
    cell.add_param_values(params)
    extractor.secrets = extractor.extract_cell_secrets(cell.original_source)
    cell.add_secrets(extractor.secrets)

    node = ConverterReactFlowChart.get_node(
        node_id,
        title,
        set(extractor.ins),
        set(extractor.outs),
        extractor.params,
        extractor.secrets,
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

    return cell
