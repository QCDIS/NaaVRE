import hashlib
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Cell:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    title               : str
    task_name           : str
    original_source     : str
    base_image          : str
    inputs              : list
    outputs             : list
    params              : list
    confs               : dict
    dependencies        : list
    chart_obj           : dict
    node_id             : str
    container_source    : str
    global_conf         : dict

    def __init__(
            self,
            title,
            task_name,
            original_source,
            inputs,
            outputs,
            params,
            confs,
            dependencies,
            container_source,
            chart_obj=None,
            node_id='',
    ) -> None:

        self.title              = title
        self.task_name          = task_name
        self.original_source    = original_source
        self.inputs             = list(inputs)
        self.outputs            = list(outputs)
        self.params             = list(params)
        self.confs              = confs
        self.types              = dict()
        self.dependencies       = dependencies
        self.chart_obj          = chart_obj
        self.node_id            = node_id
        self.container_source   = container_source

    def clean_code(self):

        indices_to_remove = []
        lines = self.original_source.splitlines()
        self.original_source = ""

        for line_i in range(0, len(lines)):

            line = lines[line_i]
            if line.startswith('import') or \
                    line.startswith('from') or \
                    line.startswith('#') or \
                    line.startswith('param_'):
                indices_to_remove.append(line_i)

        for ir in sorted(indices_to_remove, reverse=True):
            lines.pop(ir)

        self.original_source = "\n".join(lines)

    def integrate_configuration(self):

        lines = self.original_source.splitlines()
        self.original_source = ""

        for idx, conf in enumerate(self.generate_configuration()):
            lines.insert(idx, conf)

        self.original_source = "\n".join(lines)

    def generate_dependencies(self):
        resolves = []
        for d in self.dependencies:
            resolve_to = "import %s" % d['name']
            if d['module']:
                resolve_to = "from %s %s" % (d['module'], resolve_to)
            if d['asname']:
                resolve_to += " as %s" % d['asname']
            resolves.append(resolve_to)
        return resolves

    def generate_configuration(self):
        resolves = []
        for c in self.confs:
            resolves.append(self.confs[c])
        return resolves

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
