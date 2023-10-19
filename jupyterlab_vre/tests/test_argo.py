import json
import os

import requests
from unittest import TestCase

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'


class ArgoTest(TestCase):

    def test_argo_api(self):
        argo_workflow_path = os.path.join(base_path, 'workflows', 'argo')
        argo_workflow_files = os.listdir(argo_workflow_path)
        for argo_workflow_file in argo_workflow_files:
            argo_workflow_file_path = os.path.join(argo_workflow_path, argo_workflow_file)
            self.submit_argo_workflow(argo_workflow_file_path)

    def submit_argo_workflow(self, argo_workflow_path):
        ago_ns = 'argo'
        self.assertIsNotNone(os.getenv('ARGO_URL'), 'ARGO_URL not set')
        argo_api_url = os.getenv('ARGO_URL') + '/api/v1/workflows/' + ago_ns
        with open(argo_workflow_path, 'r') as read_file:
            workflow = json.load(read_file)
        token = os.getenv('ARGO_API_TOKEN')
        self.assertIsNotNone(token, 'ARGO_API_TOKEN not set')

        resp_submit = requests.post(
            argo_api_url,
            json=workflow,
            headers={
                'Authorization': token
            }
        )
        self.assertEqual(200, resp_submit.status_code, resp_submit.text)

        resp_submit_data = resp_submit.json()
        self.assertIsNotNone(resp_submit_data['metadata']['name'], 'No workflow name returned')
        resp_detail = requests.get(
            f"{argo_api_url}/{resp_submit_data['metadata']['name']}",
            json=workflow,
            headers={
                'Authorization': token
            }
        )
        self.assertEqual(200, resp_detail.status_code, resp_detail.text)
        resp_detail_data = resp_detail.json()
        self.assertTrue('metadata' in resp_detail_data)
        self.assertTrue('name' in resp_detail_data['metadata'])
