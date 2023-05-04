import re
import rpy2.robjects.packages as rpackages
import pandas as pd
from rpy2.robjects import r
import tempfile
import os
import rpy2.robjects as robjects
import rpy2.rinterface as rinterface
from rpy2.robjects.packages import importr
import re

# Load the base R package for parsing and evaluation
base = importr('base')

# TODO: create an interface such that it can be easily extended to other kernels

class RExtractor:
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
        for s in sources: # loop through every cell
            packages = []

            ''' Approach 1: Simple regex.
                this matches the following cases: require(pkg), library(pkg), library("pkg"), library(package=pkg), library(package="pkg")
            '''
            # packages = re.findall(r'(?:library|require)\((?:package=)?(?:")?(\w+)(?:")?\)', s)
            
            ''' Approach 2: Static analysis using 'renv' package.
                this approach is more safe as it covers more cases and checks comments
            '''
            with tempfile.NamedTemporaryFile(delete=False, suffix='.R') as tmp_file:
                tmp_file.write(s.encode())
                tmp_file.flush()
                renv = rpackages.importr('renv')
                function_list = renv.dependencies(tmp_file.name)
                packages = list(pd.DataFrame(function_list).transpose().iloc[:, 1])
                tmp_file.close()
                os.remove(tmp_file.name)
            
            # format the packages
            for package in packages:
                imports[package] = { # TODO: check these properties
                    'name': package,
                    'asname': '',
                    'module': '' 
                }
        return imports

    def __extract_configurations(self, sources): 
        configurations = {}
        for s in sources:
            # Parse the script using rpy2's parse() function with keep.source = TRUE
            parsed_expr = base.parse(text=s, keep_source=True) 

            # Convert the expression to a Python object using rpy2's conversion functions
            parsed_expr_py = robjects.conversion.rpy2py(parsed_expr)
            lines = s.splitlines()

            # Loop through the first level of the AST
            for expr in parsed_expr_py:

                # Check for a specific type. otherwise continue
                if not isinstance(expr, rinterface.LangSexpVector):
                    continue

                # check for matches
                c = str(expr[0])
                variable = str(expr[1]) 

                # Only look at assignments, check = or <- # TODO: is there a better way to check if it is an assignment
                if not ((c == "<-" or c == "=") and variable.split("_")[0] == "conf"):
                    continue
                
                # find the line
                for line in lines:
                    matches = re.findall(r'{}\s*(=|<-)'.format(variable), line)
                    
                    if len(matches) > 0 and variable not in configurations:
                        configurations[variable] = line
                        break
                        
        print(configurations)
        return configurations


    def __extract_params(self, sources): # TODO: naive way of extracting params, look at the AST (source https://adv-r.hadley.nz/expressions.html)
        params = set()
        for s in sources:
            # Find all variable assignments with a prefix of "param"
            pattern = r"param_[a-zA-Z0-9_]{0,}"
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
