[![make](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml/badge.svg)](https://github.com/QCDIS/NaaVRE/actions/workflows/make.yml)


# Usage

NaaVRE is a JupyterLab extension that allows users to containerize notebook cells, compose workflows based on these cells 
and run workflows on the cloud.

For more detailed information, please refer to the [documentation](https://github.com/QCDIS/vre_documetation#readme).


# Development 



## Create the conda environment

Install Requirements: 

Install Anaconda from these instructions: https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-20-04/

Close the terminal and start a new one to activate conda.

Create and activate conda environment:
```shell
conda env update -f environment.yml
```

## Build the extension

Go to the project folder and run make :
```shell
make install-backend && make build-frontend && make install-ui && make link-ui
```
Build the extension  and start a jupyterlab instance:
- Replace the ~/workspace dir with the location of your NaaVRE repo
- Get an export_VARS file with the right configuration:
```shell
source export_VARS && jupyter lab build && cp -r ~/workspace/NaaVRE/docker/repo_utils/ /tmp/ && ~/workspace/NaaVRE/docker/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*' --collaborative
```

## Make a release

Build wheel file for release:
```shell
make release
```

## Testing

To run existing tests:
```shell
python docker/repo_utils/conf_vl_repos.py  --force=True
pip install --upgrade build
pytest --ignore=docker --ignore=cypress
```


### Cypress

```shell
docker run -it -v $PWD:/e2e -w /e2e cypress/included:12.17.2
```

To run interactive mode setup X11 according to https://www.baeldung.com/linux/docker-container-gui-applications.
Then type 
```shell
 docker run -it --rm --network host -v ~/.Xauthority:/root/.Xauthority:ro -e DISPLAY=$DISPLAY  -v $PWD:/e2e -w /e2e --entrypoint '' cypress/included:12.17.2  npx cypress open . 
 ```
## Running the development environment


Setup (once, after creating the conda environment):

```shell
pip install --no-deps -e .; jupyter serverextension enable --py jupyterlab_vre --user; make build-frontend && make install-ui && make link-ui
```

Start Jupyter lab:

```shell
source export_VARS && cp -r ./docker/repo_utils/ /tmp/ && ./docker/init_script.sh && jupyter lab --autoreload --watch --NotebookApp.ip='127.0.0.1'
```

Reload frontend extension changes

```shell
# If all extensions were updated:
make build-frontend
# If a single extension was updated (eg. vre-panel):
npx lerna run build --scope @jupyter_vre/vre-panel
```

The Jupyter lab server should pick up the changes to the frontend extensions, and you just have to reload the browser tab. If Jupyter lab doesn’t pickup the changes, it needs to be restarted.


## to create new test

Create cell from UI. Then get cell json from `/tmp/wf`.



## Add new test notebooks

In the test_handlers the `test_execute_workflow_handler` tests all workflows in the test/resources/workflows/NaaVRE folder.
To add a new test workflow first you'll need to created it manually in the NaaVRE UI and then copy it to the test folder.

To do that:
1. Run make and build the extension and  start a Jupyterlab as described in [Build the extension](#build-the-extension) section. Make sure that you set the environment variables `DEBUG=true`
2. Open the NaaVRE UI and dockerize the cells that will make up the workflow.
3. Open the Workflow Manager and construct the workflow. 

After these steps go to `/tmp/workflow_cells/cells` and copy the files from that folder in the `test/resources/cells` 
folder.

To test the code in the cell you must add a `example_inputs` field to the cell file that will have to match it's input
parameters . For example:
```json
    "example_inputs" : [
    "--id",
    "0",
    "--msg",
    "Hello World!"
  ]
```

If you don't want to run the cell's code you can add a `"skip_exec": true` field to the cell file. For example:
```json
    "skip_exec": true
```

This is useful if the base installation don't contain the libraries or dependencies required by the cell's code i.e. 
lasefarm or vol2bird.

Do the same for the workflow file in `/tmp/workflow_cells/workflows` and copy it to `test/resources/workflows/NaaVRE`.
Then run the tests as described in the [Testing](#testing) section. 

This will case all cells in the `test/resources/cells` folder to be dockerized. Next all the workflows in the 
`test/resources/workflows/NaaVRE` folder will be submitted to the Argo Workflow engine.

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
```[values.yaml](..%2F..%2F..%2F..%2Fmnt%2Ffry%2Fk8s%2Fwebdav%2Fvalues.yaml)

Next, sett up the Anaconda environment:
    
```shell    
conda env update --file environment.yml
```


## Docker 

### Build the docker image

```shell
docker build -t n-a-a-vre .
```

```commandline
docker run -it -p 8888:8888 --env-file ~/Downloads/notbooks/docker_VARS n-a-a-vre /bin/bash -c "source /venv/bin/activate && /tmp/init_script.sh && jupyter lab --debug --watch --NotebookApp.token='' --NotebookApp.ip='0.0.0.0' --NotebookApp.allow_origin='*' --collaborative"
```
