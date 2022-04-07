from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.faircell import Cell
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WorkflowParser:
    logger = logging.getLogger(__name__)

    # TODO: Fix deps clones

    nodes: dict
    links: dict
    splitters: dict
    dependencies: dict
    cells_in_use: dict

    def __init__(self, nodes, links):

        self.nodes = nodes
        self.links = links

        # TODO: Use og_node_id as index for non special nodes, id for the special ones

        self.dependencies = {
            nodes[node]['id']: [] for node in nodes
        }

        self.cells_in_use = {
            nodes[node]['id']: Catalog.get_cell_from_og_node_id(nodes[node]['properties']['og_node_id'])
            for node in nodes if nodes[node]['type'] != 'splitter' and nodes[node]['type'] != 'merger'
        }

        self.__parse_links()

    def __parse_links(self):

        for k in self.links:

            link = self.links[k]

            to_node = self.nodes[link['to']['nodeId']]
            from_node = self.nodes[link['from']['nodeId']]

            from_special_node = (from_node['type'] == 'merger' or from_node['type'] == 'splitter')
            task_name = f'{from_node["type"]}_{from_node["id"][:7]}' if from_special_node else Catalog.get_cell_from_og_node_id(
                self.__get_og_node_id(from_node['id']))['task_name']

            self.dependencies[to_node['id']].append({
                'task_name': task_name,
                'port_id': link['from']['portId'],
                'type': from_node['type']
            })

    def __get_og_node_id(self, node_id) -> str:
        return self.nodes[node_id]['properties']['og_node_id']

    def get_workflow_cells(self) -> dict:
        return self.cells_in_use

    def get_dependencies_dag(self) -> dict:
        return self.dependencies
