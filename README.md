[![make release](https://github.com/QCDIS/NaaVRE/actions/workflows/make-release.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make-release.yml)
[![make](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml)


# Usage

NaaVRE is a JupyterLab extension that allows users to containerize notebook cells, compose workflows based on these cells 
and run workflows on the cloud.

For more detailed information, please refer to the [documentation](https://github.com/QCDIS/vre_documetation#readme).


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
source export_VARS && jupyter lab build && cp -r ~/workspace/NaaVRE/docker/repo_utils/ /tmp/ && ~/workspace/NaaVRE/docker/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*' --collaborative
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
conda env update --file environment.yml
```


## Docker 

```commandline
docker run -it -p 8888:8888 --env-file ~/Downloads/notbooks/docker_VARS qcdis/n-a-a-vre-laserfarm /bin/bash -c "source /venv/bin/activate && /tmp/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*' --collaborative"
```


# Argo Workflows

## Generate Token

```shell
kubectl apply -f - <<EOF
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: vre-api
  namespace: argo
rules:
  - verbs:
      - get
      - watch
      - patch
    apiGroups:
      - ''
    resources:
      - pods
  - verbs:
      - get
      - watch
    apiGroups:
      - ''
    resources:
      - pods/log
  - verbs:
      - create
    apiGroups:
      - ''
    resources:
      - pods/exec
  - verbs:
      - list
      - watch
      - create
      - get
      - update
      - delete
    apiGroups:
      - argoproj.io
    resources:
      - workflowtasksets
      - workflowartifactgctasks
      - workflowtemplates
      - workflows
  - verbs:
      - patch
    apiGroups:
      - argoproj.io
    resources:
      - workflowtasksets/status
      - workflowartifactgctasks/status
      - workflows/status
EOF
```

```shell
kubectl create sa vre-api -n argo
```

```shell
kubectl create rolebinding vre-api --role=vre-api --serviceaccount=argo:vre-api -n argo
```

```shell
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  namespace: argo
  name: vre-api.service-account-token
  annotations:
    kubernetes.io/service-account.name: vre-api
type: kubernetes.io/service-account-token
EOF
```

```shell
ARGO_TOKEN="Bearer $(kubectl get secret vre-api.service-account-token -n argo -o=jsonpath='{.data.token}' | base64 --decode)"
```

```shell
echo -n $ARGO_TOKEN | base64 -w 0
```


## Cypress 

```commandline  
docker run -it -v $PWD:/e2e -w /e2e cypress/included:12.9.0
```