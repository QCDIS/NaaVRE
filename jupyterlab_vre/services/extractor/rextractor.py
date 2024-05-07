import os
import re
import tempfile

import rpy2.rinterface as rinterface
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.packages import importr

# Import ANTLR R parser
from .parseR.parsing import parse_text
from .parseR.ExtractImports import ExtractImports
from .parseR.ExtractConfigs import ExtractConfigs
from .parseR.ExtractParams import ExtractParams
from .parseR.ExtractNames import ExtractNames

from .extractor import Extractor


# Create an R environment
r_env = robjects.globalenv

# This R code is used to obtain all assignment variables (source https://adv-r.hadley.nz/expressions.html)
r_env["result"] = robjects.r("""
library(rlang)
library(lobstr)
library(purrr)

expr_type <- function(x) {
  if (rlang::is_syntactic_literal(x)) {
    "constant"
  } else if (is.symbol(x)) {
    "symbol"
  } else if (is.call(x)) {
    "call"
  } else if (is.pairlist(x)) {
    "pairlist"
  } else {
    typeof(x)
  }
}

switch_expr <- function(x, ...) {
  switch(expr_type(x),
    ...,
    stop("Don't know how to handle type ", typeof(x), call. = FALSE)
  )
}

recurse_call <- function(x) {
  switch_expr(x,
    # Base cases
    symbol = ,
    constant = ,

    # Recursive cases
    call = ,
    pairlist =
  )
}

logical_abbr_rec <- function(x) {
  switch_expr(x,
    constant = FALSE,
    symbol = as_string(x) %in% c("F", "T")
  )
}

logical_abbr <- function(x) {
  logical_abbr_rec(enexpr(x))
}

find_assign_rec <- function(x) {
  switch_expr(x,
    constant = ,
    symbol = character()
  )
}
find_assign <- function(x) unique(find_assign_rec(enexpr(x)))

flat_map_chr <- function(.x, .f, ...) {
  purrr::flatten_chr(purrr::map(.x, .f, ...))
}

find_assign_rec <- function(x) {
  switch_expr(x,
    # Base cases
    constant = ,
    symbol = character(),

    # Recursive cases
    pairlist = flat_map_chr(as.list(x), find_assign_rec),
    call = {
      if (is_call(x, "<-") || is_call(x, "=")) { # TODO: also added is_call(x, "=") here
        if (typeof(x[[2]]) == "symbol"){ # TODO: added the type check here
            as_string(x[[2]])
        }
      } else {
        flat_map_chr(as.list(x), find_assign_rec)
      }
    }
  )
}
""")

# Load the base R package for parsing and evaluation
base = importr('base')


# TODO: create an interface such that it can be easily extended to other kernels

class RExtractor(Extractor):
    sources: list
    imports: dict
    configurations: dict
    global_params: dict
    undefined: dict

    def __init__(self, notebook, cell_source):
        self.sources = [nbcell.source for nbcell in notebook.cells if
                        nbcell.cell_type == 'code' and len(nbcell.source) > 0]
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

                # transpose renv dependencies to readable dependencies
                transposed_list = list(map(list, zip(*function_list)))
                packages = [row[1] for row in transposed_list]
                tmp_file.close()
                os.remove(tmp_file.name)

            # format the packages
            for package in packages:
                imports[package] = {
                    # asname and module are specific to Python packages. So you can probably leave them out here
                    'name': package,
                    'asname': '',
                    'module': ''
                }
        return imports

    def __extract_configurations(self, sources):
        configurations = {}
        for s in sources:
            parsed_expr = base.parse(text=s, keep_source=True)
            parsed_expr_py = robjects.conversion.rpy2py(parsed_expr)
            lines = s.splitlines()

            # loop through all assignment variables
            assignment_variables = self.assignment_variables(s)
            for variable in assignment_variables:

                # the prefix should be 'conf'
                if not (variable.split("_")[0] == "conf"):
                    continue

                # find the line of the assignment. (TODO) this approach assumes that there is only one expression in one line.
                # this might not work when we have something like: a <- 3; b = 7
                for line in lines:
                    matches = re.findall(r'{}\s*(=|<-)'.format(variable), line)

                    if len(matches) > 0 and variable not in configurations:
                        configurations[variable] = line
                        break
        return configurations

    def __extract_params(self, sources):  # check source https://adv-r.hadley.nz/expressions.html)
        params = {}
        for s in sources:
            lines = s.splitlines()

            '''Approach 1: Naive way
            Find all variable assignments with a prefix of "param"'''
            # pattern = r"param_[a-zA-Z0-9_]{0,}"
            # matches = re.findall(pattern, s) 
            # Extract the variable names from the matches
            # for match in matches:
            # params.add(match)

            '''Approach 2: Look at the AST'''
            assignment_variables = self.assignment_variables(s)
            for variable in assignment_variables:

                # the prefix should be 'param'
                if not (variable.split("_")[0] == "param"):
                    continue

                # find the line of the assignment. (TODO) this approach assumes that there is only one expression in one line.
                # this might not work when we have something like: a <- 3; b = 7
                param_value = ''
                for line in lines:
                    m = re.match(r'{}\s*(?:=|<-)(.*?)\s*(#.*?)?$'.format(variable), line)
                    if m:
                        param_value = m.group(1).strip(" \"' ")

                params[variable] = {
                    'name': variable,
                    'type': None,
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
        # TODO: check this code, you have removed logic. 
        # we probably like to only use dependencies that are necessary to execute the cell
        # however this is challenging in R as functions are non-scoped
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

    def get_function_parameters(self, cell_source):
        result = []

        # Approach 1: Naive Regex
        functions = re.findall(r'function\s*\((.*?)\)', cell_source)
        for params in functions:
            result.extend(re.findall(r'\b\w+\b', params))

        # Approach 2: AST based
        # TODO

        return list(set(result))

    def get_iterator_variables(self, cell_source):
        result = []

        # Approach 1: Naive Regex. This means that iterator variables are in the following format:
        # for ( <IT_VAR> .....)
        result = re.findall(r'for\s*\(\s*([a-zA-Z0-9.]+)\s+in', cell_source)

        # Approach 2: Parse AST. Much cleaner option as iterator variables can appear in differen syntaxes.
        # TODO

        return result

    def __extract_cell_names(self, cell_source):
        parsed_r = robjects.r['parse'](text=cell_source)
        vars_r = robjects.r['all.vars'](parsed_r)

        # Challenge 1: Function Parameters
        function_parameters = self.get_function_parameters(cell_source)
        vars_r = list(filter(lambda x: x not in function_parameters, vars_r))

        # Challenge 2: Built-in Constants
        built_in_cons = ["T", "F", "pi", "is.numeric", "mu", "round"]
        vars_r = list(filter(lambda x: x not in built_in_cons, vars_r))

        # Challenge 3: Iterator Variables
        iterator_variables = self.get_iterator_variables(cell_source)
        vars_r = list(filter(lambda x: x not in iterator_variables, vars_r))

        # Challenge 4: Apply built-in functions
        # MANUALLY SOLVED

        # Challenge 5: Libraries
        vars_r = list(filter(lambda x: x not in self.imports, vars_r))

        # Challenge 6: Variable-based data access
        # MANUALLY SOLVED

        vars_r = {
            name: {
                'name': name,
                'type': None,
            }
            for name in vars_r
        }

        return vars_r

    # This is a very inefficient approach to obtain all assignment variables (Solution 1)
    def recursive_variables(self, my_expr, result):
        if isinstance(my_expr, rinterface.LangSexpVector):
            # check if there are enough data values. for an assignment there must be three namely VARIABLE SYMBOL VALUE. e.g. a = 3
            if len(my_expr) >= 3:

                # check for matches
                c = str(my_expr[0])
                variable = my_expr[1]

                # Check if assignment. 
                if (c == "<-" or c == "="):
                    if isinstance(my_expr[1], rinterface.SexpSymbol):
                        result.add(str(variable))
        try:
            for expr in my_expr:
                result = self.recursive_variables(expr, result)
        except Exception as e:
            pass
        return result

    def assignment_variables(self, text):
        result = []

        # Solution 1 (Native-Python): Write our own recursive function that in Python that parses the Abstract Syntax Tree of the R cell
        # This is a very inefficient solution
        # parsed_expr = base.parse(text=text, keep_source=True)
        # parsed_expr_py = robjects.conversion.rpy2py(parsed_expr)
        # result = list(self.recursive_variables(parsed_expr_py, set()))

        # Solution 2 (Native-R): Use built-in recursive cases of R (source https://adv-r.hadley.nz/expressions.html). This method is significantly faster.
        output_r = robjects.r("""find_assign({
            %s
        })""" % text)
        result = re.findall(r'"([^"]*)"', str(output_r))

        # Return the result
        return result

    def __extract_cell_undefined(self, cell_source):
        # Approach 1: get all vars and substract the ones with the approach as in
        cell_names = self.__extract_cell_names(cell_source)
        assignment_variables = self.assignment_variables(cell_source)
        undef_vars = set(cell_names).difference(set(assignment_variables))

        # Approach 2: (TODO) dynamic analysis approach. this is complex for R as functions 
        # as they are not scoped (which is the case in python). As such, we might have to include
        # all the libraries to make sure that those functions work

        undef_vars = {
            name: {
                'name': name,
                'type': None,
            }
            for name in undef_vars
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
