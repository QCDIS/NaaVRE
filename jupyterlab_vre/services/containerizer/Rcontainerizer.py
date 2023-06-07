import os
import logging
from jinja2 import Environment, PackageLoader


# TODO: create an interface for other programming languages

def get_type(value):
    if value == "str" or value == "list":
        return "character"
    elif value == "int":
        return "integer"
    elif value == "float":
        return "numeric"
    else:
        raise ValueError("Not a valid type")


logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


class Rcontainerizer:

    @staticmethod
    def get_files_info(cell=None, image_repo=None, cells_path=None):
        if not os.path.exists(cells_path):
            os.mkdir(cells_path)
        cell_path = os.path.join(cells_path, cell.task_name)

        cell_file_name = cell.task_name + '.R'
        dockerfile_name = 'Dockerfile.' + image_repo + '.' + cell.task_name

        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.mkdir(cell_path)

        cell_file_path = os.path.join(cell_path, cell_file_name)
        dockerfile_file_path = os.path.join(cell_path, dockerfile_name)
        return {'cell': {
            'file_name': cell_file_name,
            'path': cell_file_path},
            'dockerfile': {
                'file_name': dockerfile_name,
                'path': dockerfile_file_path}
        }

    @staticmethod
    def build_templates(cell=None, files_info=None):
        # we also want to always add the id to the input parameters
        inputs = cell.inputs
        types = cell.types
        inputs.append('id')
        types['id'] = 'str'
        logger.debug("inputs: " + str(cell.inputs))
        logger.debug("types: " + str(cell.types))
        logger.debug("params: " + str(cell.params))
        logger.debug("outputs: " + str(cell.outputs))

        logger.debug('files_info: ' + str(files_info))
        logger.debug('cell.dependencies: ' + str(cell.dependencies))

        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)

        template_cell = template_env.get_template('R_cell_template.jinja2')
        template_dockerfile = template_env.get_template(
            'dockerfile_template_conda.jinja2')

        compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                                             confs=cell.generate_configuration())
        cell.container_source = compiled_code

        template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                             confs=cell.generate_configuration()).dump(files_info['cell']['path'])
        template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
            files_info['dockerfile']['path'])
        # set_conda_deps, set_pip_deps = map_dependencies(dependencies=cell.dependencies)
        # template_conda = template_env.get_template('conda_env_template.jinja2')
        # template_conda.stream(base_image=cell.base_image, conda_deps=list(set_conda_deps),
        #                       pip_deps=list(set_pip_deps)).dump(files_info['environment']['path'])
