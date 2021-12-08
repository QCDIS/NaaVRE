![Docker](https://github.com/qcdis-sdia/sdia-provisioner/workflows/Docker/badge.svg)
# Jupyter Lab VRE

Jupyter Lab extension for virtual research environments.

---
**NOTE**

The extension is currently under an early stage of development. This repository should not be regarded as official channel for the latest stable version, but only as reference for code updates and general information.

---
# Getting started with JupyterLab

# Installation

At the moment, the extension is only distributed on demand as a python wheel package compatible with JupyterLab >= 3.0.0. Moreover, a Docker image with the extension pre-installed is also made available.

## Pip
Create a python virtual environment 

```console
python3 -m venv  venv/
source venv/bin/activate
```
Install pip and wheel requirements

```console
pip install --upgrade pip
pip install wheel setuptools_rust
pip install jupyterlab_vre-1.0.0-py3-none-any.whl
```

Install and enable the extension
```console
pip install jupyterlab_vre-1.0.0-py3-none-any.whl
jupyter lab build 
jupyter serverextension enable --py jupyterlab_vre --user
```
Start Jupyter lab 
```console
jupyter lab 
```

## Docker

If you have ![Docker installed](https://docs.docker.com/get-docker/), you can use the NaaVRE Jupyter Docker extension. 

```console
docker run -it -p 8888:8888 qcdis/n-a-a-vre:latest jupyter lab --debug
```
This command pulls the qcdis/n-a-a-vre image Docker Hub if it is not already present on the local host. It then starts a 
container running a Jupyter Notebook server and exposes the server on host port 8888. The server logs appear in the 
terminal where you can find the server's URL e.g. http://127.0.0.1:8888/lab?token=a70292d8b2ef97ee9f873663b85b7988455cc72d68bf8df9

Additionally, it is possible to start the extension instance on a local directory as follows:

```console
docker run -it -p 8888:8888 -v <local-dir>/:/home/jovyan/work -w /home/jovyan/work qcdis/jupyterlab_vre:latest jupyter lab --debug
```

# Build Release
```bash
make release 
```

# Set up Repository for Cells
NaaVRE makes use of Git repositories write the cell code and build the corresponding containers. It also uses docker 
registries to push these images, so they can be discovered by the Argo workflow engine.   
## GitHub \& Dockerhub
### Dockerhub

1. If you don't already have a Dockerhub account create a new one.
2. Go to ![https://hub.docker.com/settings/security](https://hub.docker.com/settings/security) and create a new access token by pressing "New Access Token".


---
**IMPORTANT**
Make sure you temporarily note the access token. You're going to need it later when creating the GitHub repository. 
---
More information on Dockerhub's access tokens can be found ![here](https://docs.docker.com/docker-hub/access-tokens/)

### GitHub
1. If you don't already have a GitHub account create a new one
2. Got to the ![NaaVRE-cells](https://github.com/QCDIS/NaaVRE-cells) template repository and press on the top left on "Use 
this template"
3. Select a name for the repository make sure it's public and press "Create repository form template"

More information on template GitHub repositories can be found 
![here](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)

The newly crated GitHub repository needs to get access to DockerHub registry to push the containers generated form the code 
in the cells. To do that:
1. On the newly crated GitHub repository press "Settings" on the top left 
2. On the bottom right select "Secrets"
3. On the new page on the top left press "New repository secret" 
4. On the "Name" add "DOCKERHUB_USERNAME" and the "Value" your DockerHub username and press "Add secret"
5. On the new page on the top left press again "New repository secret"
6. On the "Name" add "DOCKERHUB_PASSWORD" and the "Value" your DockerHub access token generated from step 2 in Section "Dockerhub" and press "Add secret"


NaaVRE needs to commit the cells from your notebooks into the newly crated repository. To do that you'll need to generate 
a personal access token. To do that go to ![https://github.com/settings/tokens](https://github.com/settings/tokens). 
 1. In the top right corner select "Generate new token". 
 2. In the next page type a name for the token e.g. NaaVRE. 
 3. Set a reasonable expiration date e.g. 60. Note if this token respires you can always create a new in the future.
 4. On the section "Select scopes" tick the "repo" selection 
 5. Scroll on the bottom of the page and press "Generate token"
---
**IMPORTANT**
Make sure you temporarily note the token. You're going to need to added to NaaVRE
---
More information on GitHub's personal tokens can be found ![here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

# Argo workflow engine
Argo Workflows is an open source container-native workflow engine for orchestrating parallel jobs on Kubernetes.
## Run Argo workflow engine in minikube 
You'll need to install ![minikube](https://minikube.sigs.k8s.io/docs/start/)