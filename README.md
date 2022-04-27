[![make](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml)
[![make release](https://github.com/QCDIS/NaaVRE/actions/workflows/make-relese.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make-relese.yml)
# Getting started with NaaVRE

This is a quick start guide to use the NaaVRE.


https://user-images.githubusercontent.com/9680609/162855203-2e8f6d7e-883d-4646-aff7-c56c0f507f32.mp4



## Log in to NaaVRE

Go to one of the deployed NaaVREs
Click on 'Sign in'

<img src="https://user-images.githubusercontent.com/9680609/162737176-40a0f99c-914a-430e-9722-d09b9e564fb5.png" width="50%" height="50%">


To login select the GitHub option 

<img src="https://user-images.githubusercontent.com/9680609/162738248-02ad6183-c0cc-47c3-8872-f88652e55343.png" width="50%" height="50%">


Select the 'Latest version of VL'  and click Start.

<img src="https://user-images.githubusercontent.com/9680609/162750631-b29ca350-e5b5-4399-a6b1-704c4a15872e.png" width="50%" height="50%">

## Configure GitHub Token

On the top menu select 'LifeWatch VRE->Manage Credentials->GitHub'. Add the GitHub url and token you created from the template project at: https://github.com/QCDIS/NaaVRE-cells 

<img src="https://user-images.githubusercontent.com/9680609/164538604-b91c3c00-4760-44c3-8477-371c54951ec0.png" width="50%" height="50%">



https://user-images.githubusercontent.com/9680609/164538758-d34f6d4c-5231-4f7e-a1d0-94cab83e9fce.mp4


## Download sample notebook 

From the section 'Other' click on 'Terminal'  
<img src="https://user-images.githubusercontent.com/9680609/162739524-e200f407-6efb-4748-a863-4c95bf310f86.png" width="50%" height="50%">


In the new terminal type:
```
wget https://raw.githubusercontent.com/QCDIS/lifewatch-notebooks/main/eEcolidar/laserfarm_retiling.ipynb
```

<img src="https://user-images.githubusercontent.com/9680609/162740015-ec2d5554-6c6a-4c3b-a4cd-b7c2270adced.png" width="50%" height="50%">


You will notice a new notebook is downloaded. Close the terminal. 

<img src="https://user-images.githubusercontent.com/9680609/162744015-b19408dd-35e3-4a5a-a178-ca21b7f3d63e.png" width="50%" height="50%">


## Containerize notebook cells 


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

