![Docker](https://github.com/qcdis-sdia/sdia-provisioner/workflows/Docker/badge.svg)
# Jupyter Lab VRE

Jupyter Lab extension for virtual research environments.

---

**NOTE**

The extension is currently under an early stage of development.

---

# Getting started with NaaVRE

This is a quick start guide to run the NaaVRE in a local environment without any cloud resources.

## Start JupyterLab with NaaVRE

Make sure you have docker ![Docker installed](https://docs.docker.com/get-docker/). 

Start the NaaVRE Jupyter Docker extension:
```console
docker run -it -p 8888:8888 qcdis/n-a-a-vre:latest jupyter lab --debug
```
The server logs appear in the terminal where you can find the server's URL e.g. 
http://127.0.0.1:8888/lab?token=a70292d8b2ef97ee9f873663b85b7988455cc72d68bf8df9

## Set up Repositories for Cells

NaaVRE makes use of Git repositories write the cell code and build the corresponding containers. It also uses docker 
registries to push these images, so they can be discovered by the Argo workflow engine.   

### Dockerhub

If you don't already have a Dockerhub account create a new one.

Go to ![https://hub.docker.com/settings/security](https://hub.docker.com/settings/security) and create a new access 
token by pressing "New Access Token".


---
**IMPORTANT**

Make sure your temporarily note the access token. You're going to need it later when creating the GitHub repository. 

---
More information on Dockerhub's access tokens can be found ![here](https://docs.docker.com/docker-hub/access-tokens/)

### GitHub
If you don't already have a GitHub account create a new one

Got to the ![NaaVRE-cells](https://github.com/QCDIS/NaaVRE-cells) template repository and press on the top left on "Use 
this template"

Select a name for the repository make sure it's public and press "Create repository form template"

More information on template GitHub repositories can be found 
![here](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)

The newly crated GitHub repository needs to get access to DockerHub registry to push the containers generated form the 
code in the cells.

On the newly crated GitHub repository press "Settings" on the top left

On the bottom right select "Secrets"

On the new page on the top left press "New repository secret" 

On the "Name" add "DOCKERHUB_USERNAME" and the "Value" your DockerHub username and press "Add secret"

On the new page on the top left press again "New repository secret"

On the "Name" add "DOCKERHUB_PASSWORD" and the "Value" your DockerHub access token generated from step 2 in Section "Dockerhub" and press "Add secret"


NaaVRE needs to commit the cells from your notebooks into the newly crated repository. To do that you'll need to generate 
a personal access token. To do that go to ![https://github.com/settings/tokens](https://github.com/settings/tokens). 

In the top right corner select "Generate new token". 

In the next page type a name for the token e.g. NaaVRE. 

Set a reasonable expiration date e.g. 60. Note if this token respires you can always create a new in the future.

On the section "Select scopes" tick the "repo" selection 

Scroll on the bottom of the page and press "Generate token"

---
**IMPORTANT**

Make sure your temporarily note the token. You're going to need to added to NaaVRE

---
More information on GitHub's personal tokens can be found ![here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

## Argo workflow engine in minikube 
NaaVRE exports workflows as Argo workflows. Argo Workflows is an open source container-native workflow engine for 
orchestrating parallel jobs on Kubernetes.

Install ![minikube](https://minikube.sigs.k8s.io/docs/start/)

Install ![helm](https://helm.sh/docs/intro/install/)

Add the Argo Chart repository:
```console
helm repo add argo https://argoproj.github.io/argo-helm
```

Install the Argo workflow engine:
```console
helm install argowf argo/argo-workflows --set controller.containerRuntimeExecutor=k8sapi --set server.enabled=true --set server.serviceType=NodePort
```
Check that argo is running by typing: 
```console
kubectl get pods 
```
You will see something like:
```console
NAME                                                             READY   STATUS              RESTARTS   AGE
pod/argowf-argo-workflows-server-957d9db7d-zl7ps                 0/1     ContainerCreating   0          43s
pod/argowf-argo-workflows-workflow-controller-856464db85-4v9lx   0/1     ContainerCreating   0          43s
```

After some minutes if you run again:
```console
kubectl get pods 
```

the lines should change to:  
```console
NAME                                                             READY   STATUS    RESTARTS   AGE
pod/argowf-argo-workflows-server-957d9db7d-zl7ps                 1/1     Running   0          3m27s
pod/argowf-argo-workflows-workflow-controller-856464db85-4v9lx   1/1     Running   0          3m27s
```

Get the Argo server port by typing:
```console
kubectl get service argowf-argo-workflows-server --output='jsonpath="{.spec.ports[0].nodePort}"' && echo 
```

Now you need to find the IP address minikube is running at by typing :
```console
minikube ip
```
You should get something like:
```console
192.168.49.2
```

To open Argo server open your borrower at http://<MINIKUBE_IP>:<ARGO_PORT>

The page should ask you for an "argo auth token". To generate it type:
```console
kubectl create role vre --verb=list,update --resource=workflows.argoproj.io  && kubectl create sa vre && kubectl create rolebinding vre --role=vre --serviceaccount=argo:vre
```

And to get the argo auth token:
```console
SECRET=$(kubectl get sa vre -o=jsonpath='{.secrets[0].name}') && ARGO_TOKEN="Bearer $(kubectl get secret $SECRET -o=jsonpath='{.data.token}' | base64 --decode)" && echo $ARGO_TOKEN
```
The output should look like this:
```console
Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImJHbmc5b1l0R2p3cEhIYVJxWDY2SEZTQXVNQ3FMZWhfN3UtVVdlaDNTaFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InZyZS10b2tlbi1zOGJmYiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJ2cmUiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJjYTI1MTU4Zi1hNmVjLTQyOTEtOTM5OS05OTMwZTBiZGU2ODQiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDp2cmUifQ.vB25wrOf3OIa1ixh-VjLjew84DLvcSsroDtqSUKV3mDHm8CRv9ITGQferGIFj3A8YaZ59hPGwidAwYmhILqIsfr2oLyyF9qt7ua9uw3f7fSCSnEKGbKbpP1_J-z992MYpsv3E5kCQeUf2IOnXP7Hd4K2hdHZHQkVVrqlwWD6RaPGe4O-Mbeq1_2QD8_75F2tj3NGeyMosJCAjyG7hU3hcNu2HjLOIpvD88GjOLHk8IT4pVHYNQAkly3DLin_4os0_FT1Qt7OD3f6GIFE-0GL4BJqDKvD0-CtBoI1G16oBfR2qusY3Ow
```

Copy the entire token and pasted on the box provided at http://<MINIKUBE_IP>:<ARGO_PORT>

## Run simple workflow

Open your browser to the JupyterLab e.g. http://127.0.0.1:8888/lab?token=a70292d8b2ef97ee9f873663b85b7988455cc72d68bf8df9.
On the top you should see a tab named "LifeWatch VRE". Select "Manage Credentials"->"GitHub". In the text box 
add your GitHub token and press "save".

Create a new Python notebook and add two simple cells. Make sure you add a comment on the top for the name of each cell.
For example:
```Python
#simple-cell1
a = 40
```
```Python
#simple-cell2
b = a + 2
```  
From the mid-left select the "LifeWatch Panel" and select the output as Integer and press "ADD TO CATALOG".
You should see a message: "Local Catalog Cell successfully added to the catalog". Press ok and repeat the same 
for the other cell.

Next, got to your GitHub repository and select actions. You should see the "Docker Image CI" actions for the cells.
As soon as the actions are completed you can check if the Docker images are pushed in your Docker Hub registry.

Now you can compose your workflow from the cells you just created. Open a new Launcher in Jupyter Hub (Ctr+Shift+L).
At the bottom of the page press "Experiment Manager". There you can drag and drop the two cells you created on the 
composer canvas. Connect cell1 to cell2 and press "Export Workflow". 

If you open the File Browser (Ctr+Shift+F) you'll see a file named "workflow.yaml". Open that file and copy it's contents.

Open your browser to the Argo workflow server e.g. http://192.168.49.2:30832/ and 

## Error Reporting 
If you encounter any issues, bugs, or errors you may report them at: https://github.com/QCDIS/NaaVRE/issues/new/choose 
From there press the "Get started" button to submit a report.

Alternafilly you may use this Google form: https://docs.google.com/forms/d/e/1FAIpQLScytqOAdsizGwvwVf0q7jfmvnelvrN6PGD7_U0cnUurc1-v2g/viewform?usp=sf_link


# Build Release
```console
python3 -m venv  venv/
source venv/bin/activate
```

```console
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
make release 
```


# Installation

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
```

Install and enable the extension
```console
pip install jupyterlab_vre-py3-none-any.whl
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
