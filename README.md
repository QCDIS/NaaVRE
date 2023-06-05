[![make](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml)
[![make release](https://github.com/QCDIS/NaaVRE/actions/workflows/make-relese.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make-relese.yml)
# Getting started with NaaVRE

This is a quick start guide to use the NaaVRE.

https://user-images.githubusercontent.com/9680609/175041369-3af397d9-8b2c-40fa-a639-d643a9d15abf.mp4


## Log in to NaaVRE

Go to one of the deployed NaaVREs
Click on 'Sign in'

<img src="https://user-images.githubusercontent.com/9680609/162737176-40a0f99c-914a-430e-9722-d09b9e564fb5.png" width="50%" height="50%">

## Containerize notebook cells 


Open the notebook. Next on the left click on the LifeWatch panel.

<img src="https://user-images.githubusercontent.com/9680609/162744335-eea6a0bd-14d5-4ed4-b678-c01e3b71188e.png" width="50%" height="50%">

Select a cell.

<img src="https://user-images.githubusercontent.com/9680609/162744821-fffaa346-2aa9-4e8f-9894-d54bc1928096.png" width="50%" height="50%">

On the 'Inputs and Outputs' of the Component containerizer select the types and base image as shown below. When all the types are added 
click 'CREATE'

<img src="https://user-images.githubusercontent.com/9680609/175019281-9f5ac9c7-15fb-49ac-a62c-ef121d2b4949.png" width="50%" height="50%">

You can repeat the same for all the notebook's cell.

----

## NOTE 

When you click 'CREATE' you may get the following warning:

<img src="https://user-images.githubusercontent.com/9680609/175019467-2ea32a3c-b8b3-4db8-9533-15a1146d264c.png" width="50%" height="50%">

 To solve this go delete the base image and selected it again. 

----


## Construct Workflow 

Go to 'File->New Launcher'. On the bottom section 'LifeWatch VRE' click on the 'Experiment Manager'.

<img src="https://user-images.githubusercontent.com/9680609/175019723-84b7abd6-b23d-4b4e-acd5-b2f085ad01ce.png" width="50%" height="50%">

Open the catalog with the exported cells.

<img src="https://user-images.githubusercontent.com/9680609/175020246-25367cb6-90ae-44b1-9b73-1c863f6001bf.png" width="50%" height="50%">

Select the cell you want to add in your workpiece and clik 'ADD TO WORKSPACE'

<img src="https://user-images.githubusercontent.com/9680609/175020686-1b25f571-62f9-46c8-88b5-a74697286af5.png" width="50%" height="50%">

By dragging and dropping the cells on the left, construct the workflow shown bellow. 

<img src="https://user-images.githubusercontent.com/9680609/175020879-2ee6a0d6-21f6-497d-9b5d-616e58de7730.png" width="50%" height="50%">


Click on 'EXPORT WORKFLOW' and go to the File Browser by selecting the icon on the top left. 

<img src="https://user-images.githubusercontent.com/9680609/175021742-93c6a411-d5f2-4646-a097-474ffae2edb5.png" width="50%" height="50%">

There you should see a file named 'workflow.yaml'. If you open it, it should look like this:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: workflow-test-
spec:
    entrypoint: workflow-test
    arguments:
      parameters:
      - name: param_max_filesize
        value: ''
      - name: param_laz_compression_factor
        value: ''
      - name: param_remote_path_ahn
        value: ''
      - name: param_password
        value: ''
      - name: param_hostname
        value: ''
      - name: param_login
        value: ''
      - name: param_remote_path_root
        value: ''
    templates:
    - name: workflow-test
      dag:
        tasks:
        - name: fetch-laz-files-6c966b7
          template: fetch-laz-files-6c966b7-tmp
          arguments:
            parameters:
            - {name: param_login, value: "{{workflow.parameters.param_login}}"}
            - {name: param_password, value: "{{workflow.parameters.param_password}}"}
            - {name: param_hostname, value: "{{workflow.parameters.param_hostname}}"}
            - {name: param_remote_path_ahn, value: "{{workflow.parameters.param_remote_path_ahn}}"}
        - name: splitter-4c8b03b
          dependencies: [ fetch-laz-files-6c966b7 ]
          template: splitter-4c8b03b-tmp
          arguments:
            parameters:
            - {name: laz_files_c8e452d, value: "{{tasks.fetch-laz-files-6c966b7.outputs.parameters.laz_files_c8e452d}}"}
        - name: split-big-files-482e36f
          dependencies: [ splitter-4c8b03b ]
          template: split-big-files-482e36f-tmp
          arguments:
            parameters:
            - {name: splitter_target_4c8b03b, value: "{{item}}"}
            - {name: param_max_filesize, value: "{{workflow.parameters.param_max_filesize}}"}
            - {name: param_laz_compression_factor, value: "{{workflow.parameters.param_laz_compression_factor}}"}
            - {name: param_remote_path_ahn, value: "{{workflow.parameters.param_remote_path_ahn}}"}
            - {name: param_password, value: "{{workflow.parameters.param_password}}"}
            - {name: param_hostname, value: "{{workflow.parameters.param_hostname}}"}
            - {name: param_login, value: "{{workflow.parameters.param_login}}"}
            - {name: param_remote_path_root, value: "{{workflow.parameters.param_remote_path_root}}"}
          withParam: "{{tasks.splitter-4c8b03b.outputs.parameters.splitter_target_4c8b03b}}"

    - name: fetch-laz-files-6c966b7-tmp
      outputs:
        parameters:
          - name: laz_files_c8e452d
            valueFrom:
              path: /tmp/laz_files_c8e452d.json
      container:
        image: "qcdis/fetch-laz-files"
        command: ["/bin/bash", "-c"]
        args:
          - source /venv/bin/activate; python fetch-laz-files.py
            --param_login "{{workflow.parameters.param_login}}"
            --param_password "{{workflow.parameters.param_password}}"
            --param_hostname "{{workflow.parameters.param_hostname}}"
            --param_remote_path_ahn "{{workflow.parameters.param_remote_path_ahn}}"
            --id "c8e452d";
    - name: splitter-4c8b03b-tmp
      inputs:
        parameters:
        - name: laz_files_c8e452d
      outputs:
        parameters:
          - name: splitter_target_4c8b03b
            valueFrom:
              path: /tmp/splitter_target_4c8b03b.json
      script:
        image: python:alpine3.9
        command: [python]
        source: |
          import json
          laz_files_c8e452d = {{inputs.parameters.laz_files_c8e452d}}
          f_out = open("/tmp/splitter_target_4c8b03b.json", "w")
          f_out.write(json.dumps(laz_files_c8e452d))
          f_out.close()
    - name: split-big-files-482e36f-tmp
      inputs:
        parameters:
        - name: splitter_target_4c8b03b
        - name: param_max_filesize
        - name: param_laz_compression_factor
        - name: param_remote_path_ahn
        - name: param_password
        - name: param_hostname
        - name: param_login
        - name: param_remote_path_root
      outputs:
        parameters:
          - name: split_laz_files_947f5fa
            valueFrom:
              path: /tmp/split_laz_files_947f5fa.json
      container:
        image: "qcdis/split-big-files"
        command: ["/bin/bash", "-c"]
        args:
          - source /venv/bin/activate; python split-big-files.py
            --laz "{{inputs.parameters.splitter_target_4c8b03b}}"
            --param_max_filesize "{{workflow.parameters.param_max_filesize}}"
            --param_laz_compression_factor "{{workflow.parameters.param_laz_compression_factor}}"
            --param_remote_path_ahn "{{workflow.parameters.param_remote_path_ahn}}"
            --param_password "{{workflow.parameters.param_password}}"
            --param_hostname "{{workflow.parameters.param_hostname}}"
            --param_login "{{workflow.parameters.param_login}}"
            --param_remote_path_root "{{workflow.parameters.param_remote_path_root}}"
            --id "947f5fa";
```

Download that file on your own machine. 

## Execute the workflow

Go to the Argo workflow engine and click on the workflow templates.

<img src="https://user-images.githubusercontent.com/9680609/162761426-7616a345-b1f3-48b3-b7d9-06eae7e1f75f.png" width="50%" height="50%">

Click on the 'CREATE NEW WORKFLOW TEMPLATE' and upload the workflow.yaml file and click '+CREATE'

<img src="https://user-images.githubusercontent.com/9680609/162762038-ca469845-57ec-4579-b6e9-2801f9557fa5.png" width="50%" height="50%">


Now click on '+ SUBMIT'

<img src="https://user-images.githubusercontent.com/9680609/162762394-e6839f7f-8e95-4775-9425-cdbbeaa28b3b.png" width="50%" height="50%">


Fill in the perimeters as shown below and the necessary webdav credentials and click '+ SUBMIT'

<img src="https://user-images.githubusercontent.com/9680609/175022341-793c574e-0841-421e-835f-c27216b3b8b9.png" width="50%" height="50%">

When the workflow completes its execution  it should look like this:

<img src="https://user-images.githubusercontent.com/9680609/175033417-44e16626-5a73-449a-88af-2cf21f0599e5.png" width="50%" height="50%">


# Development 


## Summary 

1. Create conda venv
2. Install requirements in conda 
3. Install nodejs dependencies
4. make build-frontend
5. make build-frontend && make install-ui && make link-ui
6. make install-backend 
7. jupyter lab build
8. Restart jupyter jupyter lab --debug  

## Create conda venv

Install Requirements: 

Install Anaconda from these instructions: https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-20-04/

Close the terminal and start a new one to activate conda.

Create and activate conda environment:
```shell
conda env update -f environment.yml
```

Clone project:
```shell
git clone https://github.com/QCDIS/NaaVRE.git
```

Create and checkout branch:
```shell
cd NaaVRE
git branch <BRANCH_NAME>
git checkout <BRANCH_NAME>
```

Go to the project folder and run make :

Build the backend and frontend:
```shell
make install-backend && make build-frontend && make install-ui && make link-ui
```

Build the extension  and start a jupyterlab instance:
```shell
source export_VARS && jupyter lab build && cp -r ~/workspace/NaaVRE/docker/repo_utils/ /tmp/ && ~/workspace/NaaVRE/docker/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*'
```

Build wheel file for release:
```shell
make release
```

## Troubleshooting

When running make install-backend, if the following error occurs:

```python
Traceback (most recent call last):
  File "setup.py", line 2, in <module>
    from pathlib import Path
ImportError: No module named pathlib
make: *** [build-backend] Error 1
```


Removed Anaconda entirely from the machine (MacOS), and do a full reinstall as follows:

```shell
brew install anaconda
export PATH="/usr/local/anaconda3/bin:$PATH"
```

Next, sett up the Anaconda environment:
    
```shell    
conda create -n jupyterlab  python=3.9 
conda activate jupyterlab
```


## Docker 

```commandline
docker run -it -p 8888:8888 --env-file ~/Downloads/notbooks/docker_VARS qcdis/n-a-a-vre-laserfarm /bin/bash -c "source /venv/bin/activate && /tmp/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*'"
```
