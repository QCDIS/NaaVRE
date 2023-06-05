import json
import json
import os
import subprocess
import sys
from pathlib import Path
from time import sleep
from unittest import mock

import requests
from github import Github
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, ExportWorkflowHandler, ExecuteWorkflowHandler, \
    NotebookSearchHandler, NotebookSearchRatingHandler
from jupyterlab_vre.component_containerizer.handlers import find_job
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.handlers import load_module_names_mapping
from jupyterlab_vre.notebook_search.handlers import NotebookDownloadHandler

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'

cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')


def delete_all_cells():
    for cell in Catalog.get_all_cells():
        print(cell)
        Catalog.delete_cell_from_title(cell['title'])


def get_gh_repository():
    cat_repositories = Catalog.get_repositories()

    print(cat_repositories)
    assert cat_repositories is not None
    assert len(cat_repositories) >= 1

    gh = Github(cat_repositories[0]['token'])
    owner = cat_repositories[0]['url'].split('https://github.com/')[1].split('/')[0]
    repository_name = cat_repositories[0]['url'].split(
        'https://github.com/')[1].split('/')[1]
    if '.git' in repository_name:
        repository_name = repository_name.split('.git')[0]
    return gh.get_repo(owner + '/' + repository_name)


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
        with mock.patch.object(ExportWorkflowHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/get_files.json')
            # with open(workflow_path, 'r') as read_file:
            #     payload = json.load(read_file)
            # response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))
            # response.

    def test_execute_workflow_handler(self):
        with mock.patch.object(ExecuteWorkflowHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/simple_workflow.json')
            with open(workflow_path, 'r') as read_file:
                payload = json.load(read_file)
            response = self.fetch('/executeworkflowhandler', method='POST', body=json.dumps(payload))
            json_response = json.loads(response.body.decode('utf-8'))

    def test_load_module_names_mapping(self):
        load_module_names_mapping()

    def test_extractor_handler_MULTIPLY(self):
        with mock.patch.object(ExportWorkflowHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'notebooks/MULTIPLY_framework_2.json')
            # with open(workflow_path, 'r') as read_file:
            #     payload = json.load(read_file)
            # response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))

    def test_search_handler(self):
        with mock.patch.object(NotebookSearchHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'keyword': 'explosion'}
            # response = self.fetch('/notebooksearch', method='POST', body=json.dumps(payload))
            # json_response = json.loads(response.body.decode('utf-8'))
            # self.assertIsNotNone(json_response)


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
            self.assertEqual(response.code, 200)

    def test_notebook_download_handler(self):
        with mock.patch.object(NotebookSearchRatingHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'docid': 'Kaggle219', 'notebook_name': 'Laserfarm.ipynb'}
            response = self.fetch('/notebookdownloadhandler', method='POST', body=json.dumps(payload))
            self.assertEqual(response.code, 200)

    def test_cells_handler(self):
        with mock.patch.object(CellsHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            cells_json_path = os.path.join(base_path, 'cells')
            cells_files = os.listdir(cells_json_path)
            for cell_file in cells_files:
                print(cell_file)
                cell_path = os.path.join(cells_json_path, cell_file)
                with open(cell_path, 'r') as file:
                    cell = json.load(file)
                file.close()
                test_cell = Cell(cell['title'], cell['task_name'], cell['original_source'], cell['inputs'],
                                 cell['outputs'],
                                 cell['params'], cell['confs'], cell['dependencies'], cell['container_source'],
                                 cell['chart_obj'], cell['node_id'])
                test_cell.types = cell['types']
                test_cell.base_image = cell['base_image']
                Catalog.editor_buffer = test_cell
                response = self.fetch('/cellshandler', method='POST', body=json.dumps(''))
                self.assertEqual(200, response.code)
                wf_id = json.loads(response.body.decode('utf-8'))['wf_id']
                cell_path = os.path.join(cells_path, test_cell.task_name, test_cell.task_name + '.py')

                cell_exec = subprocess.Popen([sys.executable, cell_path, '--id', '0', '--split_laz_files', '[file]'],
                                             stdout=subprocess.PIPE)
                print('---------------------------------------------------')
                text = cell_exec.communicate()[0]
                print(text)
                print("stdout:", cell_exec.stdout)
                print("stderr:", cell_exec.stderr)
                print("returncode:", cell_exec.returncode)
                print('---------------------------------------------------')
                self.assertEqual(0, cell_exec.returncode, text)
                cat_repositories = Catalog.get_repositories()
                repo_token = cat_repositories[0]['token']
                owner = cat_repositories[0]['url'].split('https://github.com/')[1].split('/')[0]
                repository_name = cat_repositories[0]['url'].split(
                    'https://github.com/')[1].split('/')[1]
                if '.git' in repository_name:
                    repository_name = repository_name.split('.git')[0]

                sleep(200)
                job = find_job(wf_id=wf_id, owner=owner, repository_name=repository_name, token=repo_token, job_id=None)
                self.assertIsNotNone(job, 'Job not found')
                done = False
                counter = 0
                while counter < 50:
                    counter += 1
                    print('--------------------------------------------------------')
                    print(job['status'])
                    sleep(60)

                    job = find_job(wf_id=wf_id, owner=owner, repository_name=repository_name, token=repo_token,
                                   job_id=job['id'])
                    if job['status'] == 'completed':
                        done = True
                        break
                self.assertEqual('completed', job['status'], 'Job not completed')
                self.assertEqual('success', job['conclusion'], 'Job not successful')

    def test_argo_api(self):
        argo_workflow_path = os.path.join(base_path, 'workflows/argo_workflow2.json')
        self.submit_workflow(argo_workflow_path)

    def submit_workflow(self,argo_workflow_path):
        ago_ns = 'argo'
        self.assertIsNotNone(os.getenv('ARGO_URL'), 'ARGO_URL not set')
        ARGO_API_URL = os.getenv('ARGO_URL') + '/api/v1/workflows/' + ago_ns
        with open(argo_workflow_path, 'r') as read_file:
            workflow = json.load(read_file)
        token = os.getenv('ARGO_API_TOKEN')
        self.assertIsNotNone(token, 'ARGO_API_TOKEN not set')

        resp_submit = requests.post(
            ARGO_API_URL,
            json=workflow,
            headers={
                'Authorization': token
            }
        )
        self.assertEqual(200, resp_submit.status_code, resp_submit.text)

        resp_submit_data = resp_submit.json()
        self.assertIsNotNone(resp_submit_data['metadata']['name'], 'No workflow name returned')
        resp_detail = requests.get(
            f"{ARGO_API_URL}/{resp_submit_data['metadata']['name']}",
            json=workflow,
            headers={
                'Authorization': token
            }
        )
        self.assertEqual(200, resp_detail.status_code, resp_detail.text)
        resp_detail_data = resp_detail.json()
