import re
from pyflakes import reporter as pyflakes_reporter, api as pyflakes_api
import ast


class Extractor:
    sources: list
    imports: list
    configurations: dict
    global_params: set
    undefined: set

    def __init__(self, notebook):
        self.sources = [nbcell.source for nbcell in notebook.cells if
                        nbcell.cell_type == 'code' and len(nbcell.source) > 0]

        self.imports = self.__extract_imports(self.sources)
        self.configurations = self.__extract_configurations(self.sources)
        self.global_params = self.__extract_params(self.sources)
        self.undefined = set()
        for source in self.sources:
            self.undefined.update(self.__extract_cell_undefined(source))

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
                            configurations[name] = lines[node.lineno - 1]
        return self.__resolve_configurations(configurations)

    def __extract_params(self, sources):
        params = set()
        for s in sources:
            tree = ast.parse(s)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and hasattr(node.targets[0], 'id'):
                    name = node.targets[0].id
                    prefix = name.split('_')[0]
                    if prefix == 'param':
                        params.add(name)
        return params

    def infere_cell_outputs(self, cell_source):
        cell_names = self.__extract_cell_names(cell_source)
        return [name for name in cell_names if name not in self.__extract_cell_undefined(cell_source) \
                and name not in self.imports and name in self.undefined and name not in self.configurations and name not in self.global_params]

    def infere_cell_inputs(self, cell_source):
        cell_undefined = self.__extract_cell_undefined(cell_source)
        return [und for und in cell_undefined if
                und not in self.imports and und not in self.configurations and und not in self.global_params]

    def infer_cell_dependencies(self, cell_source, confs):
        dependencies = []
        names = self.__extract_cell_names(cell_source)

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

    def __extract_cell_names(self, cell_source):
        names = set()
        tree = ast.parse(cell_source)
        for module in ast.walk(tree):
            if isinstance(module, (ast.Name,)):
                names.add(module.id)
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
        undef_vars = set()

        for line in filter(lambda a: a != '\n' and 'undefined name' in a, out):
            var_search = re.search(p, line)
            undef_vars.add(var_search.group(1))
        return undef_vars

    def extract_cell_params(self, cell_source):
        cell_unds = self.__extract_cell_undefined(cell_source)
        return self.global_params.intersection(cell_unds)

    def extract_cell_conf_ref(self, cell_source):
        confs = {}
        cell_unds = self.__extract_cell_undefined(cell_source)
        conf_unds = [und for und in cell_unds if und in self.configurations]
        for u in conf_unds:
            if u not in confs:
                confs[u] = self.configurations[u]
        return confs

    def __resolve_configurations(self, configurations):
        confs_in_assignment = {}
        resolved_configurations = {}
        for conf_name in configurations:
            conf = configurations[conf_name]
            if 'conf_' in conf.split('=')[1]:
                confs_in_assignment[conf_name] = conf
        for conf_name in configurations:
            for confs_in_assignment_name in confs_in_assignment:
                if conf_name in confs_in_assignment[confs_in_assignment_name] and conf_name not in resolved_configurations:
                    replace_value = configurations[conf_name].split('=')[1]
                    if confs_in_assignment_name in resolved_configurations:
                        new_value = resolved_configurations[confs_in_assignment_name].replace(conf_name,replace_value)
                    else:
                        new_value = confs_in_assignment[confs_in_assignment_name].replace(conf_name,replace_value)
                    resolved_configurations[confs_in_assignment_name] = new_value
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
