from jupyterlab_vre.component_containerizer.handlers import ExtractorHandler, TypesHandler, BaseImageHandler
from jupyterlab_vre.credentials.handlers import CredentialsHandler
from jupyterlab_vre.experiment_manager.handlers import ExportWorkflowHandler
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from ._version import __version__ 
from notebook.utils import url_path_join
from .handlers import CellsHandler, CatalogGetAllHandler, ProvisionAddHandler


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_vre"
    }]


def load_jupyter_server_extension(lab_app):

    host_pattern = '.*$'

    lab_app.web_app.add_handlers(host_pattern, [
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/extract'), ExtractorHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/types'), TypesHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/containerizer/baseimage'), BaseImageHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/credentials'), CredentialsHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/cells'), CellsHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/cells/all'), CatalogGetAllHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/provision/add'), ProvisionAddHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/expmanager/export'), ExportWorkflowHandler)
    ])
    
    lab_app.log.info("Registered FAIR-Cells extension at URL path /vre")
