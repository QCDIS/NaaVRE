import json
import os
import subprocess
from unittest import mock
import sys
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from pathlib import Path
from subprocess import Popen, PIPE

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, ExportWorkflowHandler, ExecuteWorkflowHandler, \
    NotebookSearchHandler, NotebookSearchRatingHandler
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.handlers import load_module_names_mapping
from jupyterlab_vre.notebook_search.handlers import NotebookDownloadHandler

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'


def delete_all_cells():
    for cell in Catalog.get_all_cells():
        print(cell)
        Catalog.delete_cell_from_title(cell['title'])


class HandlersAPITest(AsyncHTTPTestCase):

    def get_app(self):
        notebook_path = os.path.join(base_path, 'notebooks/test_notebook.ipynb')
        with open(notebook_path, mode='r', encoding='utf-8') as f:
            self.notebook_dict = json.load(f)
        self.app = Application([('/extractorhandler', ExtractorHandler),
                                ('/typeshandler', TypesHandler),
                                ('/cellshandler', CellsHandler),
                                ('/exportworkflowhandler', ExportWorkflowHandler),
                                ('/executeworkflowhandler', ExecuteWorkflowHandler),
                                ('/notebooksearch', NotebookSearchHandler),
                                ('/notebooksearchratinghandler', NotebookSearchRatingHandler),
                                ('/notebookdownloadhandler', NotebookDownloadHandler),
                                ],
                               cookie_secret='asdfasdf')
        return self.app

    def test_export_workflow_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/get_files.json')
            # with open(workflow_path, 'r') as read_file:
            #     payload = json.load(read_file)
            # response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))

    def test_execute_workflow_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/laserfarm.json')
            # with open(workflow_path, 'r') as read_file:
            #     payload = json.load(read_file)
            # response = self.fetch('/executeworkflowhandler', method='POST', body=json.dumps(payload))

    def test_load_module_names_mapping(self):
        load_module_names_mapping()

    def test_extractor_handler_MULTIPLY(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'notebooks/MULTIPLY_framework_2.json')
            # with open(workflow_path, 'r') as read_file:
            #     payload = json.load(read_file)
            # response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))

    def test_search_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'keyword': 'explosion'}
            response = self.fetch('/notebooksearch', method='POST', body=json.dumps(payload))
            json_response = json.loads(response.body.decode('utf-8'))
            self.assertIsNotNone(json_response)

    def test_search_rating_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {"keyword": "math",
                       "notebook": {"docid": "D1089", "name": "student-performance-in-exams", "source": "Kaggle",
                                    "html_url": "https://www.kaggle.com/code/spscientist/student-performance-in-exams",
                                    "description": "# Students performance in exams\n#### Marks secured by the students in college\n## Aim\n#### To understand the influence of various factors like economic, personal and social on the students performance \n## Inferences would be : \n#### 1. How to imporve the students performance in each test ?\n#### 2. What are the major factors influencing the test scores ?\n#### 3. Effectiveness of test preparation course?\n#### 4. Other inferences \n#### Import the required libraries\n#### Let us initialize the required values ( we will use them later in the program )\n#### we will set the minimum marks to 40 to pass in a exam\n#### Let us read the data from the csv file\n#### We will print top few rows to understand about the various data columns\n#### Size of data frame\n#### Let us understand about the basic information of the data, like min, max, mean and standard deviation etc.\n#### Let us check for any missing values\n##### As seen above, there are no missing ( null ) values in this dataframe but in real scenarios we need work on dataset with a lot of missing values  \n####  Let us explore the Math Score first\n#### How many students passed in Math exam ?\n#### Let us explore the Reading score\n#### How many studends passed in reading ?\n#### Let us explore writing score\n#### How many students passed writing ?\n#### Iet us check \"How many students passed in all the subjects ?\"\n#### Find the percentage of marks\n#### Let us assign the grades\n### Grading \n####    above 80 = A Grade\n####      70 to 80 = B Grade\n####      60 to 70 = C Grade\n####      50 to 60 = D Grade\n####      40 to 50 = E Grade\n####    below 40 = F Grade  ( means Fail )\n#### we will plot the grades obtained in a order\n",
                                    "kaggle_id": "spscientist/student-performance-in-exams",
                                    "file_name": "student-performance-in-exams.ipynb", "rating": 4}}
            response = self.fetch('/notebooksearchratinghandler', method='POST', body=json.dumps(payload))

    def test_notebook_download_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'docid': 'Kaggle219', 'notebook_name': 'Laserfarm.ipynb'}
            response = self.fetch('/notebookdownloadhandler', method='POST', body=json.dumps(payload))

    def test_cells_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            title = 'Test-Retiling-dev-dev-skoulouzis'
            task_name = 'test-retiling-dev-skoulouzis'
            original_source = '# Retiling\nsplit_laz_files\n\nfor file in split_laz_files:\n    print(file)\n    retiler_output = file'
            inputs = {'split_laz_files'}
            outputs = {'retiler_output'}
            params = []
            confs = {'conf_min_x': "conf_min_x = '-113107.81'",
                     'conf_min_y': "conf_min_y = '214783.87'", 'conf_max_y': "conf_max_y = '726783.87'",
                     'conf_max_x': "conf_max_x = '398892.19'",
                     'conf_n_tiles_side': "conf_n_tiles_side = '512'",
                     'conf_local_tmp': "conf_local_tmp = pathlib.Path('/tmp')"}
            dependencies = [{'name': 'pathlib', 'asname': None, 'module': ''}]
            container_source = ''
            chart_obj = None
            node_id = 'fe8b944'
            types = {'split_laz_files': 'list', 'retiler_output': 'str'}

            test_cell = Cell(title, task_name, original_source, inputs, outputs, params, confs,
                             dependencies,
                             container_source, chart_obj, node_id)
            test_cell.types = types
            test_cell.base_image = 'qcdis/miniconda3-pdal'
            Catalog.editor_buffer = test_cell
            response = self.fetch('/cellshandler', method='POST', body=json.dumps(''))
            cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
            cell_path = os.path.join(cells_path, test_cell.task_name, test_cell.task_name + '.py')
            cell_exec = subprocess.Popen([sys.executable, cell_path, '--id', '0', '--split_laz_files', '[file]'],stdout=PIPE)
            print('---------------------------------------------------')
            text = cell_exec.communicate()[0]
            print(text)
            print("stdout:", cell_exec.stdout)
            print("stderr:", cell_exec.stderr)
            print("returncode:", cell_exec.returncode)
            print('---------------------------------------------------')
            self.assertEqual(0, cell_exec.returncode, 'Failed')
