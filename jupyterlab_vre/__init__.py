from notebook.utils import url_path_join
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from ._version import __version__ 

from .component_containerizer.handlers import ExtractorHandler, TypesHandler, BaseImageHandler, CellsHandler
from .experiment_manager.handlers import ExportWorkflowHandler, ExecuteWorkflowHandler
from .handlers import CatalogGetAllHandler
from .notebook_containerizer.handlers import NotebookExtractorHandler
from .notebook_search.handlers import NotebookSearchHandler
from .registries.handlers import RegistriesHandler
from .repositories.handlers import RepositoriesHandler


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_vre"
    }]


def load_jupyter_server_extension(lab_app):

    host_pattern = '.*$'

    lab_app.web_app.add_handlers(host_pattern, [
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/notebooksearch'), NotebookSearchHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/extract'), ExtractorHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/nbcontainerizer/extract'), NotebookExtractorHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/types'), TypesHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/baseimage'), BaseImageHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/addcell'), CellsHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/cells/all'), CatalogGetAllHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/expmanager/export'), ExportWorkflowHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/expmanager/execute'), ExecuteWorkflowHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/repositories/?'), RepositoriesHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/registries/?'), RegistriesHandler)
    ])
    
    lab_app.log.info("Registered NaaVRE extension at URL path /vre")
