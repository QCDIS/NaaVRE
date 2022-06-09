#!/bin/sh

conda activate jupyterlab

#make install-backend && make build-frontend && make install-ui && make link-ui
make release
cp dist/jupyterlab_vre-0.1.0-py3-none-any.whl docker/