import re
from pyflakes import reporter as pyflakes_reporter, api as pyflakes_api
import ast

# TODO: create an interface such that it can be easily extended to other kernels

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
        for s in sources: # here, we loop through every cell
            packages = re.findall(r'(?:library|require)\((?:package=)?(?:")?(\w+)(?:")?\)', s) # matches cases: require(pkg), library(pkg), library("pkg"), library(package=pkg), library(package="pkg")
            for package in packages:
                imports[package] = {
                    'name': package, # TODO: is this correct?
                    'asname': '', # TODO
                    'module': '' # TODO
                }
        return imports

    def __extract_configurations(self, sources):
        configurations = {}
        return configurations # TODO: later

    def __extract_params(self, sources): # TODO: naive way of extracting params, look at the AST (source https://adv-r.hadley.nz/expressions.html)
        params = set()
        for s in sources:
            # Find all variable assignments with a prefix of "param"
            pattern = r"param_[a-zA-Z0,9]{0,}"
            matches = re.findall(pattern, s)
            
            # Extract the variable names from the matches
            for match in matches:
                params.add(match)
        return params

    def infere_cell_outputs(self, cell_source): # TODO: check
        cell_names = self.__extract_cell_names(cell_source)
        return [name for name in cell_names if name not in self.__extract_cell_undefined(cell_source) \
                and name not in self.imports and name in self.undefined and name not in self.configurations and name not in self.global_params]

    def infere_cell_inputs(self, cell_source): # TODO: check this code, you have removed logic
        return self.global_params

    def infer_cell_dependencies(self, cell_source, confs): # TODO: check this code, you have removed logic
        dependencies = []
        for name in self.imports:
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
        names = set() # TODO: what does this code code?
        return set(names)

    def __extract_cell_undefined(self, cell_source):
        undef_vars = set() # TODO: later
        return undef_vars

    def extract_cell_params(self, cell_source): # TODO: check
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
