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
        self.splitters = defaultdict(dict)

        self.dependencies = {nodes[node]['properties']['og_node_id']: [] for node in nodes if
                             nodes[node]['type'] != 'splitter' and nodes[node]['type'] != 'merger'}
        logger.debug('self.dependencies: '+str(self.dependencies))
        self.cells_in_use = {nodes[node]['properties']['og_node_id']: \
                                 Catalog.get_cell_from_og_node_id(nodes[node]['properties']['og_node_id']) \
                             for node in nodes if nodes[node]['type'] != 'splitter' and nodes[node]['type'] != 'merger'
                             }
        self.__parse_links()
        self.__resolve_splitters()

    def __resolve_splitters(self):

        for s, links in self.splitters.items():
            og_id_to = self.__get_og_node_id(links['target']['to']['nodeId'])
            og_id_from = self.__get_og_node_id(links['source']['from']['nodeId'])
            from_cell = Catalog.get_cell_from_og_node_id(og_id_from)
            self.dependencies[og_id_to].append({
                'task_name': from_cell['task_name'],
                'port_id': links['source']['from']['portId'],
                'scaling': True
            })

    def __parse_links(self):

        '''
            node1(pno) => (sps)splitter(spt) => (pni)node2
            node1(pno) => (pni)node2
        '''

        for k in self.links:
            link = self.links[k]

            if link['to']['portId'] == 'splitter_source' or link['to']['portId'] == 'merger_source':
                self.splitters[link['to']['nodeId']]['source'] = link
                continue

            if link['from']['portId'] == 'splitter_target' or link['to']['portId'] == 'merger_target':
                self.splitters[link['from']['nodeId']]['target'] = link

            else:
                og_id_to = self.__get_og_node_id(link['to']['nodeId'])
                logger.debug('link: '+str(link['from']['nodeId']))
                og_id_from = self.__get_og_node_id(link['from']['nodeId'])
                from_cell = Catalog.get_cell_from_og_node_id(og_id_from)
                self.dependencies[og_id_to].append({
                    'task_name': from_cell['task_name'],
                    'port_id': link['from']['portId'],
                    'scaling': False
                })

    def __get_og_node_id(self, node_id) -> str:
        logger.debug('Node: ' + str(self.nodes[node_id]))
        return self.nodes[node_id]['properties']['og_node_id']

    def get_workflow_cells(self) -> dict:
        return self.cells_in_use

    def get_dependencies_dag(self) -> dict:
        return self.dependencies
