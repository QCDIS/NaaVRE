from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from ._version import __version__ 
from notebook.utils import url_path_join
from .handlers import ExtractorHandler, CellsHandler, \
    CatalogGetAllHandler, ExportWorkflowHandler, SDIAAuthHandler, \
    SDIACredentialsHandler, TypesHandler, ProvisionAddHandler, \
    GithubAuthHandler


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_vre"
    }]


def load_jupyter_server_extension(lab_app):

    host_pattern = '.*$'

    lab_app.web_app.add_handlers(host_pattern, [
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/extractor'), ExtractorHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/types'), TypesHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/sdia/testauth'), SDIAAuthHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/sdia/credentials'), SDIACredentialsHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/github/savetoken'), GithubAuthHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/cells'), CellsHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/cells/all'), CatalogGetAllHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/catalog/provision/add'), ProvisionAddHandler),
        (url_path_join(lab_app.web_app.settings['base_url'], r'/vre/workflow/export'), ExportWorkflowHandler)
    ])
    
    lab_app.log.info("Registered FAIR-Cells extension at URL path /vre")
