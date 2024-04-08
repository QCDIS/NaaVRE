import ast
import logging
import re
from functools import lru_cache

from pyflakes import reporter as pyflakes_reporter, api as pyflakes_api
from pytype import config as pytype_config
from pytype.tools.annotate_ast import annotate_ast

from .extractor import Extractor


class PyExtractor(Extractor):
    sources: list
    imports: dict
    configurations: dict
    global_params: dict
    undefined: dict

    def __init__(self, notebook, cell_source):
        # If cell_type is code and not starting with '!'
        self.sources = [nbcell.source for nbcell in notebook.cells if
                        nbcell.cell_type == 'code' and len(nbcell.source) > 0 and nbcell.source[0] != '!']
        self.notebook_names = self.__extract_cell_names(
            '\n'.join(self.sources),
            infer_types=True,
        )
        self.imports = self.__extract_imports(self.sources)
        self.configurations = self.__extract_configurations(self.sources)
        self.global_params = self.__extract_params(self.sources)
        self.undefined = dict()
        for source in self.sources:
            self.undefined.update(self.__extract_cell_undefined(source))

        super().__init__(notebook, cell_source)

    def __extract_imports(self, sources):
        imports = {}
        for s in sources:
            tree = ast.parse(s)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom,)):
                    for n in node.names:
                        key = n.asname if n.asname else n.name
                        if key not in imports:
                            imports[key] = {
                                'name': n.name,
                                'asname': n.asname or None,
                                'module': node.module if isinstance(node, ast.ImportFrom) else ""
                            }
        return imports

    def __extract_configurations(self, sources):
        configurations = {}
        for s in sources:
            lines = s.splitlines()
            tree = ast.parse(s)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    target = node.targets[0]
                    if hasattr(target, 'id'):
                        name = node.targets[0].id
                        prefix = name.split('_')[0]
                        if prefix == 'conf' and name not in configurations:
                            conf_line = ''
                            for line in lines[node.lineno - 1:node.end_lineno]:
                                conf_line += line.strip()
                            configurations[name] = conf_line
        return self.__resolve_configurations(configurations)

    def __extract_params(self, sources):
        params = dict()
        for s in sources:
            lines = s.splitlines()
            tree = ast.parse(s)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and hasattr(node.targets[0], 'id'):
                    name = node.targets[0].id
                    prefix = name.split('_')[0]
                    if prefix == 'param':
                        param_line = ''
                        for line in lines[node.lineno - 1:node.end_lineno]:
                            param_line += line.strip()
                        param_value = ast.unparse(node.value)
                        try:
                            # remove quotes around strings
                            param_value = str(ast.literal_eval(param_value))
                        except ValueError:
                            # when param_value can't safely be parsed,
                            pass
                        params[name] = {
                            'name': name,
                            'type': self.notebook_names[name]['type'],
                            'value': param_value,
                        }
        return params

    def infer_cell_outputs(self):
        cell_names = self.__extract_cell_names(self.cell_source)
        return {
            name: properties
            for name, properties in cell_names.items()
            if name not in self.__extract_cell_undefined(self.cell_source)
               and name not in self.imports
               and name in self.undefined
               and name not in self.configurations
               and name not in self.global_params
        }

    def infer_cell_inputs(self):
        cell_undefined = self.__extract_cell_undefined(self.cell_source)
        return {
            und: properties
            for und, properties in cell_undefined.items()
            if und not in self.imports
               and und not in self.configurations
               and und not in self.global_params
        }

    def infer_cell_dependencies(self, confs):
        dependencies = []
        names = self.__extract_cell_names(self.cell_source)

        for ck in confs:
            names.update(self.__extract_cell_names(confs[ck]))

        for name in names:
            if name in self.imports:
                dependencies.append(self.imports.get(name))

        return dependencies

    def infer_cell_conf_dependencies(self, confs):
        dependencies = []
        for ck in confs:
            for name in self.__extract_cell_names(confs[ck]):
                if name in self.imports:
                    dependencies.append(self.imports.get(name))

        return dependencies

    @staticmethod
    @lru_cache
    def __get_annotated_ast(cell_source):
        return annotate_ast.annotate_source(
            cell_source, ast, pytype_config.Options.create())

    def __convert_type_annotation(self, type_annotation):
        """ Convert type annotation to the ones supported for cell interfaces

        :param type_annotation: type annotation obtained by e.g. pytype
        :return: converted type: 'int', 'float', 'str', 'list', or None
        """
        if type_annotation is None:
            return None

        patterns = {
            'int': [
                re.compile(r'^int$'),
            ],
            'float': [
                re.compile(r'^float$'),
            ],
            'str': [
                re.compile(r'^str$'),
            ],
            'list': [
                re.compile(r'^List\['),
            ],
            None: [
                re.compile(r'^Any$'),
                re.compile(r'^Dict'),
                re.compile(r'^Callable'),
            ]
        }
        for type_name, regs in patterns.items():
            for reg in regs:
                if reg.match(type_annotation):
                    return type_name

        logging.getLogger(__name__).debug(f'Unmatched type: {type_annotation}')
        return None

    def __extract_cell_names(self, cell_source, infer_types=False):
        names = dict()
        if infer_types:
            tree = self.__get_annotated_ast(cell_source)
        else:
            tree = ast.parse(cell_source)
        for module in ast.walk(tree):
            if isinstance(module, (ast.Name,)):
                var_name = module.id
                if infer_types:
                    try:
                        var_type = self.__convert_type_annotation(module.resolved_annotation)
                    except AttributeError:
                        print('__extract_cell_names failed', var_name)
                        var_type = None
                else:
                    var_type = self.notebook_names[var_name]['type']
                names[module.id] = {
                    'name': var_name,
                    'type': var_type,
                }
        return names

    def __extract_cell_undefined(self, cell_source):

        flakes_stdout = StreamList()
        flakes_stderr = StreamList()
        rep = pyflakes_reporter.Reporter(
            flakes_stdout.reset(),
            flakes_stderr.reset())
        pyflakes_api.check(cell_source, filename="temp", reporter=rep)

        if rep._stderr():
            raise SyntaxError("Flakes reported the following error:"
                              "\n{}".format('\t' + '\t'.join(rep._stderr())))
        p = r"'(.+?)'"

        out = rep._stdout()
        undef_vars = dict()

        for line in filter(lambda a: a != '\n' and 'undefined name' in a, out):
            var_search = re.search(p, line)
            var_name = var_search.group(1)
            undef_vars[var_name] = {
                'name': var_name,
                'type': self.notebook_names[var_name]['type'],
            }
        return undef_vars

    def extract_cell_params(self, cell_source):
        params = {}
        cell_unds = self.__extract_cell_undefined(cell_source)
        param_unds = [und for und in cell_unds if und in self.global_params]
        for u in param_unds:
            if u not in params:
                params[u] = self.global_params[u]
        return params

    def extract_cell_conf_ref(self):
        confs = {}
        cell_unds = self.__extract_cell_undefined(self.cell_source)
        conf_unds = [und for und in cell_unds if und in self.configurations]
        for u in conf_unds:
            if u not in confs:
                confs[u] = self.configurations[u]
        return confs

    def __resolve_configurations(self, configurations):
        resolved_configurations = {}
        for k, assignment in configurations.items():
            while 'conf_' in assignment.split('=')[1]:
                for conf_name, replacing_assignment in configurations.items():
                    if conf_name in assignment.split('=')[1]:
                        assignment = assignment.replace(
                            conf_name,
                            replacing_assignment.split('=')[1],
                            )
                resolved_configurations[k] = assignment
        configurations.update(resolved_configurations)
        return configurations


class StreamList:

    def __init__(self):
        self.out = list()

    def write(self, text):
        self.out.append(text)

    def reset(self):
        self.out = list()
        return self

    def __call__(self):
        return self.out
