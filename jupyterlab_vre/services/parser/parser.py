from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.database.cell import Cell
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

        self.dependencies = {
            nodes[node]['id']: [] for node in nodes
        }
        self.cells_in_use = {}
        for node in nodes:
            if nodes[node]['type'] != 'splitter' and nodes[node]['type'] != 'merger':
                try:
                    self.cells_in_use[nodes[node]['id']] = Catalog.get_cell_from_og_node_id(
                        nodes[node]['properties']['og_node_id'])
                except Exception:
                    if 'properties' in nodes[node]:
                        raise Exception('Error while parsing ' + nodes[node]['properties']['title'])
                    elif 'properties' not in nodes[node]:
                        raise Exception('Error while parsing ' + nodes[node] + ' has no properties')
                    elif 'og_node_id' not in nodes[node]['properties']:
                        raise Exception('Error while parsing node id: ' + node + ' has no og_node_id')
                    else:
                        raise Exception('Error while parsing node id: ' + node)

        for nid, node in self.nodes.items():
            for pid, port in node['ports'].items():
                is_special = node['type'] == 'splitter' or node['type'] == 'merger'
                trailing_id = nid if is_special else node['properties']['og_node_id']
                self.nodes[nid]['ports'][pid]['id'] = f"{pid}_{trailing_id[:7]}"

        for lid, link in self.links.items():
            node_from = self.nodes[link['from']['nodeId']]
            node_to = self.nodes[link['to']['nodeId']]

            from_is_special = node_from['type'] == 'splitter' or node_from['type'] == 'merger'
            to_is_special = node_to['type'] == 'splitter' or node_to['type'] == 'merger'

            from_trailing_id = node_from['id'] if from_is_special else node_from['properties']['og_node_id']
            to_trailing_id = node_to['id'] if to_is_special else node_to['properties']['og_node_id']

            link['from']['portId'] = link['from']['portId'] + "_" + from_trailing_id[:7]
            link['to']['portId'] = link['to']['portId'] + "_" + to_trailing_id[:7]

        self.__parse_links()

    def __parse_links(self):

        for k in self.links:
            link = self.links[k]

            to_node = self.nodes[link['to']['nodeId']]
            from_node = self.nodes[link['from']['nodeId']]

            from_special_node = (from_node['type'] == 'merger' or from_node['type'] == 'splitter')

            task_name = f'{from_node["type"]}-{from_node["id"][:7]}' if from_special_node else \
                Catalog.get_cell_from_og_node_id(
                    self.__get_og_node_id(from_node['id']))['task_name'] + "-" + from_node['id'][:7]

            self.dependencies[to_node['id']].append({
                'task_name': task_name,
                'port_id': link['from']['portId'],
                'og_port_id': link['to']['portId'],
                'type': from_node['type']
            })

    def __get_og_node_id(self, node_id) -> str:
        return self.nodes[node_id]['properties']['og_node_id']

    def get_workflow_cells(self) -> dict:
        return self.cells_in_use

    def get_dependencies_dag(self) -> dict:
        return self.dependencies
