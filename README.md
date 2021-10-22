# Jupyter Lab VRE

Jupyter Lab extension for virtual research environments.

---
**NOTE**

The extension is currently under a early stage of development. This repository should not be regarded as official channel for the latest stable version, but only as reference for code updates and general information.

---

# Installation

At the moment, the extension is only distributed on demand as a python wheel package compatible with JupyterLab >= 3.0.0. Moreover, a Docker image with the extension pre-installed is also made available.

## Pip

```console
pip install jupyterlab_vre-<version>-py3-none-any.whl && jupyter lab build
```

## Docker

```console
docker run -it -p 8888:8888 qcdis/jupyterlab_vre:latest jupyter lab --debug
```

Additionally, it is possible to start the extension instance on a local directory as follows:

```console
docker run -it -p 8888:8888 -v <local-dir>/:/home/jovyan/work -w /home/jovyan/work qcdis/jupyterlab_vre:latest jupyter lab --debug
```