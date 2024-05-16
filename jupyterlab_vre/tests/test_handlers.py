import datetime
import glob
import json
import os
import random
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep
from unittest import mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, ExportWorkflowHandler, ExecuteWorkflowHandler, \
    NotebookSearchHandler, NotebookSearchRatingHandler
from jupyterlab_vre.component_containerizer.handlers import wait_for_job
from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.handlers import load_module_names_mapping
from jupyterlab_vre.notebook_search.handlers import NotebookDownloadHandler

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'

cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')

def delete_text(file_path, text_to_delete):
    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Remove the text from each line
    updated_lines = []
    for line in lines:
        updated_line = line.replace(text_to_delete, '')
        updated_lines.append(updated_line)

    # Write the updated lines to the file
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)


def delete_all_cells():
    for cell in Catalog.get_all_cells():
        print(cell)
        Catalog.delete_cell_from_title(cell['title'])


def create_cell_and_add_to_cat(cell_path=None):
    print('Creating cell from: ', cell_path)
    with open(cell_path, 'r') as file:
        cell = json.load(file)
    file.close()
    notebook_dict = {}
    if 'notebook_dict' in cell:
        notebook_dict = cell['notebook_dict']
    test_cell = Cell(cell['title'], cell['task_name'], cell['original_source'], cell['inputs'],
                     cell['outputs'],
                     cell['params'], cell['confs'], cell['dependencies'], cell['container_source'],
                     cell['chart_obj'], cell['node_id'], cell['kernel'], notebook_dict)
    test_cell.types = cell['types']
    test_cell.base_image = cell['base_image']
    Catalog.editor_buffer = test_cell
    return test_cell, cell


def wait_for_api_resource(github=None):
    # Wait for API resource
    while github.get_rate_limit().core.remaining <= 0:
        print('Github rate limit: ', github.get_rate_limit().core.remaining)
        reset = github.get_rate_limit().core.reset
        # Calculate remaining time for reset
        remaining_time = reset.timestamp() - datetime.datetime.now().timestamp()
        print('Remaining time for reset: ', divmod(remaining_time, 60))
        print('API rate exceeded, waiting')
        remaining_time = reset.timestamp() - datetime.datetime.now().timestamp()
        print('Sleeping for: ', remaining_time + 1)
        sleep(remaining_time + 1)


class HandlersAPITest(AsyncHTTPTestCase):

    os.environ["ASYNC_TEST_TIMEOUT"] = "120"

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

    def test_load_module_names_mapping(self):
        load_module_names_mapping()

    def test_search_handler(self):
        with mock.patch.object(NotebookSearchHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'keyword': 'explosion'}
            response = self.fetch('/notebooksearch', method='POST', body=json.dumps(payload))
            json_response = json.loads(response.body.decode('utf-8'))
            self.assertIsNotNone(json_response)

    def test_search_rating_handler(self):
        with mock.patch.object(NotebookSearchRatingHandler, 'get_secure_cookie') as m:
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
            test_cells = []
            for cell_file in cells_files:
                cell_path = os.path.join(cells_json_path, cell_file)
                test_cell, cell = create_cell_and_add_to_cat(cell_path=cell_path)
                response = self.call_cell_handler()
                self.assertEqual(200, response.code)
                wf_id = json.loads(response.body.decode('utf-8'))['wf_id']
                wf_creation_utc = datetime.datetime.now(tz=datetime.timezone.utc)
                dispatched_github_workflow = json.loads(response.body.decode('utf-8'))['dispatched_github_workflow']
                test_cells.append({
                    'wf_id': wf_id,
                    'wf_creation_utc': wf_creation_utc,
                    'dispatched_github_workflow': dispatched_github_workflow,
                })
                if 'skip_exec' in cell and cell['skip_exec']:
                    continue
                if 'python' in test_cell.kernel and 'skip_exec':
                    cell_path = os.path.join(cells_path, test_cell.task_name, 'task.py')
                    print('---------------------------------------------------')
                    print('Executing cell: ', cell_path)
                    if 'example_inputs' in cell:
                        exec_args = [sys.executable, cell_path] + cell['example_inputs']
                    else:
                        exec_args = [sys.executable, cell_path]

                    cell_exec = subprocess.Popen(exec_args,
                                                 stdout=subprocess.PIPE)
                    text = cell_exec.communicate()[0]
                    print(text)
                    print("stdout:", cell_exec.stdout)
                    print("stderr:", cell_exec.stderr)
                    print("return code:", cell_exec.returncode)
                    print('---------------------------------------------------')
                    self.assertEqual(0, cell_exec.returncode, 'Cell execution failed: ' + cell_file)
                elif test_cell.kernel == 'IRkernel' and 'skip_exec':
                    cell_path = os.path.join(cells_path, test_cell.task_name, 'task.R')
                    run_local_cell_path = os.path.join(cells_path, test_cell.task_name, 'run_local.R')
                    shutil.copy(cell_path, run_local_cell_path)
                    delete_text(run_local_cell_path, 'setwd(\'/app\')')
                    example_inputs = ''
                    if 'example_inputs' in cell:
                        example_inputs = ' '.join(cell['example_inputs'])
                    command = 'Rscript ' + run_local_cell_path + ' ' + example_inputs
                    result = subprocess.run(shlex.split(command), capture_output=True, text=True)
                    self.assertEqual(0, result.returncode, result.stderr)

            cat_repositories = Catalog.get_repositories()
            repo = cat_repositories[0]
            repo_token = repo['token']
            owner, repository_name = repo['url'].removeprefix('https://github.com/').split('/')
            if '.git' in repository_name:
                repository_name = repository_name.split('.git')[0]

            updated_cells = list(filter(
                lambda cell: cell['dispatched_github_workflow'],
                test_cells,
            ))

            for cell in updated_cells:
                # Get job id (many calls to the GitHub API)
                job = wait_for_job(
                    wf_id=cell['wf_id'],
                    wf_creation_utc=cell['wf_creation_utc'],
                    owner=owner,
                    repository_name=repository_name,
                    token=repo_token,
                    job_id=None,
                    timeout=300,
                    wait_for_completion=False,
                )
                cell['job'] = job

            for cell in updated_cells:
                # Wait for job completion (fewer calls)
                job = wait_for_job(
                    wf_id=cell['wf_id'],
                    wf_creation_utc=None,
                    owner=owner,
                    repository_name=repository_name,
                    token=repo_token,
                    job_id=cell['job']['id'],
                    timeout=300,
                    wait_for_completion=True,
                )
                cell['job'] = job

            for cell in updated_cells:
                self.assertIsNotNone(cell['job'], 'Job not found')
                self.assertEqual('completed', cell['job']['status'], 'Job not completed')
                self.assertEqual('success', cell['job']['conclusion'], 'Job not successful')

    def test_extractor_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            notebooks_json_path = os.path.join(base_path, 'notebooks')
            notebooks_files = glob.glob(os.path.join(notebooks_json_path, "*.json"))
            for notebook_file in notebooks_files:
                with open(notebook_file, 'r') as file:
                    notebook = json.load(file)
                file.close()
                response = self.fetch('/extractorhandler', method='POST', body=json.dumps(notebook))
                self.assertEqual(response.code, 200)
                # Get Json response
                json_response = json.loads(response.body.decode('utf-8'))
                self.assertIsNotNone(json_response)
                cell = notebook['notebook']['cells'][notebook['cell_index']]
                print('cell: ', cell)

    def test_execute_workflow_handler(self):
        workflow_path = os.path.join(base_path, 'workflows', 'NaaVRE')
        workflow_files = os.listdir(workflow_path)
        with mock.patch.object(ExecuteWorkflowHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
        cells_json_path = os.path.join(base_path, 'cells')
        cells_files = os.listdir(cells_json_path)
        for cell_file in cells_files:
            cell_path = os.path.join(cells_json_path, cell_file)
            create_cell_and_add_to_cat(cell_path=cell_path)
            response = self.call_cell_handler()
            wf_creation_utc = datetime.datetime.now(tz=datetime.timezone.utc)
            self.assertEqual(200, response.code)
            git_wf_id = json.loads(response.body.decode('utf-8'))['wf_id']
            cat_repositories = Catalog.get_repositories()
            repo = cat_repositories[0]
            repo_token = repo['token']
            owner, repository_name = repo['url'].removeprefix('https://github.com/').split('/')
            job = wait_for_job(
                wf_id=git_wf_id,
                wf_creation_utc=wf_creation_utc,
                owner=owner,
                repository_name=repository_name,
                token=repo_token,
                job_id=None,
                timeout=300,
                wait_for_completion=True,
            )
            self.assertIsNotNone(job, 'Job not found')
            self.assertEqual('completed', job['status'], 'Job not completed')
        for workflow_file in workflow_files:
            print('workflow_file: ', workflow_file)
            workflow_file_path = os.path.join(workflow_path, workflow_file)
            with open(workflow_file_path, 'r') as read_file:
                payload = json.load(read_file)

            response = self.fetch('/executeworkflowhandler', method='POST', body=json.dumps(payload))
            self.assertEqual(response.code, 200, response.body)
            json_response = json.loads(response.body.decode('utf-8'))
            self.assertIsNotNone(json_response)
            self.assertTrue('argo_id' in json_response)
            self.assertTrue('created' in json_response)
            self.assertTrue('status' in json_response)
            self.assertTrue('argo_url' in json_response)
            workflow_id = json_response['argo_id']
            response = self.fetch(f'/executeworkflowhandler?workflow_id={workflow_id}', method='GET')
            self.assertEqual(response.code, 200, response.body)
            json_response = json.loads(response.body.decode('utf-8'))
            self.assertIsNotNone(json_response)
            self.assertTrue('argo_id' in json_response)
            self.assertTrue('created' in json_response)
            self.assertTrue('status' in json_response)
            self.assertTrue('argo_url' in json_response)
            self.assertTrue('progress' in json_response)
            while json_response['status'] == 'Running':
                response = self.fetch(f'/executeworkflowhandler?workflow_id={workflow_id}', method='GET')
                self.assertEqual(response.code, 200, response.body)
                json_response = json.loads(response.body.decode('utf-8'))
                print(json.dumps(json_response, indent=2))
                self.assertIsNotNone(json_response)
                self.assertTrue('argo_id' in json_response)
                self.assertTrue('created' in json_response)
                self.assertTrue('status' in json_response)
                self.assertTrue('argo_url' in json_response)
                self.assertTrue('progress' in json_response)
                if json_response['status'] != 'Running':
                    break
                sleep(30)
            self.assertTrue(json_response['status'] == 'Succeeded', json_response)

    def call_cell_handler(self):
        response = self.fetch('/cellshandler', method='POST', body=json.dumps(''))
        return response

    def test_files_updated(self):
        with mock.patch.object(CellsHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            cells_json_path = os.path.join(base_path, 'cells')
            cells_files = os.listdir(cells_json_path)
            saved_debug_value = os.getenv("DEBUG")
            for cell_file in cells_files:
                cell_path = os.path.join(cells_json_path, cell_file)

                # Commit cell
                os.environ["DEBUG"] = "False"
                create_cell_and_add_to_cat(cell_path=cell_path)
                response = self.call_cell_handler()
                self.assertEqual(200, response.code)

                # Commit same cell again
                os.environ["DEBUG"] = "False"
                create_cell_and_add_to_cat(cell_path=cell_path)
                response = self.call_cell_handler()
                self.assertEqual(200, response.code)
                dispatched_github_workflow = json.loads(response.body.decode('utf-8'))['dispatched_github_workflow']
                self.assertFalse(dispatched_github_workflow)

                # Commit same cell again, forcing update
                os.environ["DEBUG"] = "True"
                create_cell_and_add_to_cat(cell_path=cell_path)
                response = self.call_cell_handler()
                self.assertEqual(200, response.code)
                dispatched_github_workflow = json.loads(response.body.decode('utf-8'))['dispatched_github_workflow']
                self.assertTrue(dispatched_github_workflow)

                # Commit modified cell
                _, new_cell = create_cell_and_add_to_cat(cell_path=cell_path)
                new_cell['original_source'] += f'\na = {random.random()}'
                with open(cell_path, 'r') as f:
                    saved_cell_text = f.read()
                try:
                    with open(cell_path, 'w') as file:
                        json.dump(new_cell, file, indent=2)
                    os.environ["DEBUG"] = "False"
                    create_cell_and_add_to_cat(cell_path=cell_path)
                    response = self.call_cell_handler()
                    self.assertEqual(200, response.code)
                    dispatched_github_workflow = json.loads(response.body.decode('utf-8'))['dispatched_github_workflow']
                    self.assertTrue(dispatched_github_workflow)
                finally:
                    with open(cell_path, 'w') as f:
                        f.write(saved_cell_text)

        if saved_debug_value is not None:
            os.environ["DEBUG"] = saved_debug_value
        else:
            del os.environ["DEBUG"]
