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
conda create -n jupyterlab  python=3.9 
```
Or
```shell
conda env create --name envname --file=environments.yml
conda activate rclone-data-mounter
```

## Install requirements in conda 
```shell
conda install jupyterlab nodejs yarn
conda install -c conda-forge typescript 
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

Go to the project folder and install nodejs dependencies :
```shell 
npm install lerna --force
npm install --force
```
Build the backend and frontend:
```shell
npx lerna run build --scope @jupyter_vre/core
npx lerna run build --scope @jupyter_vre/components
make install-backend && make build-frontend && make install-ui && make link-ui
```

Build the extension  and start a jupyterlab instance:
```shell
jupyter lab build && jupyter lab --debug --watch
```

Build wheel file for release:
```shell
make release
```

## Remove componetnts

First uninstall all the components:
```
make uninstall-ui && make unlink-ui
```

Then delete the relevatnt folders i.e. vre-menu

Next make install the UI compontents 

```
make build-frontend && make install-ui
```
