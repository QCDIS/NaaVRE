import os
import re
import tempfile

import rpy2.rinterface as rinterface
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.packages import importr

from .extractor import Extractor

from .parseR.parsing import parse_text
from .parseR.Visitors import *

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
        self.notebook_names = self.__extract_cell_names(
            '\n'.join(self.sources)
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

            '''Approach 3: AST parsing'''
            # tree = parse_text(s)
            # visitor = ExtractImports()
            # output = visitor.visit(tree)
            
            # for o in output:
            #     imports[o] = {
            #         'name': o,
            #         'asname': '',
            #         'module': ''
            #     }

        return imports

    def __extract_configurations(self, sources):
        configurations = {}
        for s in sources:
            tree = parse_text(s)
            visitor = ExtractConfigs()
            output = visitor.visit(tree)

            for o in output:
                configurations[o] = output[o]

        return configurations

    def __extract_params(self, sources):
        params = {}
        for s in sources:
            tree = parse_text(s)
            visitor = ExtractParams()
            output = visitor.visit(tree)

            for o in output:
                params[o] = {
                    'name': o,
                    'type': self.notebook_names[o]['type'] if o in self.notebook_names else None,
                    'value': output[o]['val']
                }

        return params

    def infer_cell_outputs(self):
        cell_names = self.__extract_cell_names(self.cell_source)
        cell_undef = self.__extract_cell_undefined(self.cell_source)
        return {
            name: properties
            for name, properties in cell_names.items()
            if name not in cell_undef
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

    def __extract_cell_names(self, cell_source):
        tree = parse_text(cell_source)
        visitor = ExtractNames()
        vars_r = visitor.visit(tree)

        return vars_r

    def __extract_cell_undefined(self, cell_source):
        tree = parse_text(cell_source)
        visitor = ExtractDefined()
        defs, scoped = visitor.visit(tree)
        visitor = ExtractUndefined(defs, scoped)
        undefs = visitor.visit(tree)

        undef_vars = {
              name: {
                  'name': name,
                  'type': self.notebook_names[name]['type'] if name in self.notebook_names else None,
              }
            for name in undefs
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