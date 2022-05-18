# Getting started with NaaVRE

## Re-Configure Git and Registry credentials

Start a new launcher and create a new notebook. 
Create a new cell and add the following command: 
```python
python conf_vl_repos.py --force=True --github_url=https://github.com/QCDIS/NaaVRE-container-prestage --github_token=SECRET_TOKEN --registry_url=https://hub.docker.com/u/qcdis
```

Note that you need to replace the SECRET_TOKEN with the git token provided to you

## Containerize notebook cells 

Go to '/examples/notebooks/eEcolidar/'. 
Open the notebook. Next on the left click on the LifeWatch panel.

<img src="https://user-images.githubusercontent.com/9680609/162744335-eea6a0bd-14d5-4ed4-b678-c01e3b71188e.png" width="50%" height="50%">

Select the 'Fetch Laz File' cell.

<img src="https://user-images.githubusercontent.com/9680609/162744821-fffaa346-2aa9-4e8f-9894-d54bc1928096.png" width="50%" height="50%">

On the 'Inputs and Outputs' of the Component containerizer select the types as shown below. When all the types are added Click 'ADD TO CATALOG'

<img src="https://user-images.githubusercontent.com/9680609/162745361-6d09440f-9ae9-434d-8ed8-a81f28865b1a.png" width="50%" height="50%">

Select the 'Retiling' cell. On the 'Inputs and Outputs' of the Component containerizer select the types as shown below. When all the types are added Click 'ADD TO CATALOG'

<img src="https://user-images.githubusercontent.com/9680609/162830069-1f0ba0a9-f068-4940-a448-100cd278c74e.png" width="50%" height="50%">


----

## NOTE 

When you click 'ADD TO CATALOG' you may get the following warning:

<img src="https://user-images.githubusercontent.com/9680609/162751191-c0000e65-9132-44c5-9967-d0a6b65c7743.png" width="50%" height="50%">

 To solve this go through all the inputs and outputs, select a different type and then back the type shown in the image above. 

----


## Construct Workflow 

Go to 'File->New Launcher'. On the bottom section 'LifeWatch VRE' click on the 'Experiment Manager'.

<img src="https://user-images.githubusercontent.com/9680609/162753068-8704c396-5391-45c5-853c-48d607df3472.png" width="50%" height="50%">

By dragging and dropping the cells on the left, construct the workflow shown bellow. 

<img src="https://user-images.githubusercontent.com/9680609/162758227-2eebddd7-3e84-490b-8df4-1c7a80c55d71.png" width="50%" height="50%">


Click on 'EXPORT WORKFLOW' and go to the File Browser by selecting the icon on the top left. 

<img src="https://user-images.githubusercontent.com/9680609/162760145-9dfcfe6a-b105-4474-badb-057d5225b6de.png" width="50%" height="50%">

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
      - name: param_login
        value: ''
      - name: param_hostname
        value: ''
      - name: param_password
        value: ''
    templates:
    - name: workflow-test
      dag:
        tasks:
        - name: fetch-laz-files-demo
          template: fetch-laz-files-demo-tmp
          arguments:
            parameters:
            - {name: param_login, value: "{{workflow.parameters.param_login}}"}
            - {name: param_hostname, value: "{{workflow.parameters.param_hostname}}"}
            - {name: param_password, value: "{{workflow.parameters.param_password}}"}
        - name: retiling-demo
          dependencies: [ fetch-laz-files-demo ]
          template: retiling-demo-tmp
          arguments:
            parameters:
            - {name: laz_files, value: "{{item}}"}
            - {name: param_login, value: "{{workflow.parameters.param_login}}"}
            - {name: param_hostname, value: "{{workflow.parameters.param_hostname}}"}
            - {name: param_password, value: "{{workflow.parameters.param_password}}"}
          withParam: "{{tasks.fetch-laz-files-demo.outputs.parameters.outs}}"

    - name: fetch-laz-files-demo-tmp
      outputs:
        parameters:
          - name: outs
            valueFrom:
              path: /tmp/outputs.json
      container:
        image: "qcdis/fetch-laz-files-demo"
        command: ["/bin/bash", "-c"]
        args:
          - source /venv/bin/activate;
            python fetch-laz-files-demo.py
            --param_login {{workflow.parameters.param_login}}
            --param_hostname {{workflow.parameters.param_hostname}}
            --param_password {{workflow.parameters.param_password}};
    - name: retiling-demo-tmp
      inputs:
        parameters:
        - name: laz_files
        - name: param_login
        - name: param_hostname
        - name: param_password
      outputs:
        parameters:
          - name: outs
            valueFrom:
              path: /tmp/outputs.json
      container:
        image: "qcdis/retiling-demo"
        command: ["/bin/bash", "-c"]
        args:
          - source /venv/bin/activate;
            echo  {{inputs.parameters.laz_files}} > /tmp/inputs.json;
            python retiling-demo.py
            --param_login {{workflow.parameters.param_login}}
            --param_hostname {{workflow.parameters.param_hostname}}
            --param_password {{workflow.parameters.param_password}};
```

Download that file on your own machine. 

## Execute the workflow

Go to the Argo workflow engine and click on the workflow templates.

<img src="https://user-images.githubusercontent.com/9680609/162761426-7616a345-b1f3-48b3-b7d9-06eae7e1f75f.png" width="50%" height="50%">

Click on the 'CREATE NEW WORKFLOW TEMPLATE' and upload the workflow.yaml file and click '+CREATE'

<img src="https://user-images.githubusercontent.com/9680609/162762038-ca469845-57ec-4579-b6e9-2801f9557fa5.png" width="50%" height="50%">


Now click on '+ SUBMIT'

<img src="https://user-images.githubusercontent.com/9680609/162762394-e6839f7f-8e95-4775-9425-cdbbeaa28b3b.png" width="50%" height="50%">


Fill in the perimeters as shown below and click '+ SUBMIT'

<img src="https://user-images.githubusercontent.com/9680609/162762707-1eba8e59-6d7b-4cc2-8bde-391863e63e5d.png" width="50%" height="50%">

When the workflow completes its execution  it should look like this:

<img src="https://user-images.githubusercontent.com/9680609/162831481-23c8a69c-1bf4-4b96-ab9d-01da6b618c72.png" width="50%" height="50%">

