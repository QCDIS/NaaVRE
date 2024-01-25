from typing import Literal, Union
import os
import re

import json
import jsonschema
import logging
import yaml


class HeaderExtractor:
    """ Extracts cells using information defined by the user in its header

    Cells should contain a comment with a yaml block defining inputs, outputs,
    params and confs. Eg:

    # My cell
    # ---
    # NaaVRE:
    #   cell:
    #     inputs:
    #       - my_input:
    #           type: String
    #       - my_other_input:
    #           type: Integer
    #     outputs:
    #       - my_output:
    #           type: List
    #     params:
    #       - param_something:
    #           type: String
    #           default_value: "my default value"
    #     confs:
    #       - conf_something_else:
    #           assignation: "conf_something_else = 'my other value'"
    # ...
    [cell code]

    The document is validated with the schema `cell_header.schema.json`

    """

    def __init__(self, notebook, cell_source):
        self.re_yaml_doc_in_comment = re.compile(
            (r"^(?:.*\n)*"
             r"\s*#\s*---\s*\n"
             r"((?:\s*#.*\n)+?)"
             r"\s*#\s*\.\.\.\s*\n"
             ),
            re.MULTILINE)
        self.schema = self._load_schema()

        self.notebook = notebook
        self.cell_source = cell_source
        self.cell_header = self._extract_header(cell_source)

    @staticmethod
    def _load_schema():
        filename = os.path.join(
            os.path.dirname(__file__),
            'cell_header.schema.json')
        with open(filename) as f:
            schema = json.load(f)
        return schema

    def enabled(self):
        return self.cell_header is not None

    def _extract_header(self, cell_source):
        # get yaml document from cell comments
        m = self.re_yaml_doc_in_comment.match(cell_source)
        if not (m and m.groups()):
            return None
        yaml_doc = m.group(1)
        # remove comment symbol
        yaml_doc = '\n'.join([
            line.lstrip().lstrip('#')
            for line in yaml_doc.splitlines()
            ])
        # parse yaml
        header = yaml.safe_load(yaml_doc)
        # validate schema
        try:
            jsonschema.validate(header, self.schema)
        except jsonschema.ValidationError as e:
            logging.getLogger().debug(f"Cell header validation error: {e}")
            raise e
        return header

    @staticmethod
    def _parse_inputs_outputs_param_items(
            item: Union[str, dict],
            item_type: Literal['inputs', 'outputs', 'params'],
            ) -> dict:
        """ Parse inputs, outputs, or params items from the header

        They can have either format
        - ElementVarName: 'my_name'
        - ElementVarNameType {'my_name': 'my_type'}
        - IOElementVarDict {'my_name': {'type': 'my_type'}}
          or ParamElementVarDict {'my_name': {'type': 'my_type',
                                              'default_value': 'my_value'}}

        Returns
        - if item_type is 'inputs' or 'outputs':
            {'name': 'my_name', 'type': 'my_type'}
        - if item_type is 'params':
            {'name': 'my_name', 'type': 'my_type', 'value': 'my_value'}
        """
        var_dict = {}

        # ElementVarName
        if isinstance(item, str):
            var_dict = {
                'name': item,
                'type': None,
                'value': None,
                }
        elif isinstance(item, dict):
            if len(item.keys()) != 1:
                # this should have been caught by the schema validation
                raise ValueError(f"Unexpected item in {item_type}: {item}")
            var_name = list(item.keys())[0]
            var_props = item[var_name]
            # ElementVarNameType
            if isinstance(var_props, str):
                var_dict = {
                    'name': var_name,
                    'type': var_props,
                    'value': None,
                    }
            # IOElementVarDict or ParamElementVarDict
            elif isinstance(var_props, dict):
                var_dict = {
                    'name': var_name,
                    'type': var_props.get('type'),
                    'value': var_props.get('default_value'),
                    }

        # Convert types
        types_conversion = {
            'Integer': 'int',
            'Float': 'float',
            'String': 'str',
            'List': 'list',
            None: None,
            }
        var_dict['type'] = types_conversion[var_dict['type']]

        # 'value' should only be kept for params
        if item_type not in ['params']:
            del var_dict['value']

        return var_dict

    def _infer_cell_inputs_outputs_params(
            self,
            source,
            item_type: Literal['inputs', 'outputs', 'params'],
            ) -> dict:
        header = self._extract_header(source)
        items = header['NaaVRE']['cell'].get(item_type, [])
        items = [self._parse_inputs_outputs_param_items(it, item_type)
                 for it in items]
        return {it['name']: it for it in items}

    def infer_cell_inputs(self, source):
        return self._infer_cell_inputs_outputs_params(source, 'inputs')

    def infer_cell_outputs(self, source):
        return self._infer_cell_inputs_outputs_params(source, 'outputs')

    def extract_cell_params(self, source):
        return self._infer_cell_inputs_outputs_params(source, 'params')

    def extract_cell_conf_ref(self, source):
        header = self._extract_header(source)
        items = header['NaaVRE']['cell'].get('confs', [])
        return {k: v['assignation'] for it in items for k, v in it.items()}

    def infer_cell_dependencies(self, source, confs):
        header = self._extract_header(source)
        items = header['NaaVRE']['cell'].get('dependencies', [])
        return [
            {
                'name': it.get('name'),
                'asname': it.get('asname', None),
                'module': it.get('module', ''),
                }
            for it in items]
