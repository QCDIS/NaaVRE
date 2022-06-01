#!/bin/sh

conda activate jupyterlab

make install-backend && make build-frontend && make install-ui && make link-ui
make release
cp ../dist/jupyterlab_vre-0.1.0-py3-none-any.whl .

sudo docker build . --file Dockerfile -t qcdis/n-a-a-vre
sudo docker build . --file Dockerfile-laserfarm -t qcdis/n-a-a-vre-laserfarm:$1
sudo docker build . --file Dockerfile-vol2bird -t qcdis/n-a-a-vre-vol2bird:$1
sudo docker build . --file Dockerfile-MULTIPLY -t qcdis/n-a-a-vre-multiply:$1
sudo docker build . --file Dockerfile-pytorch -t qcdis/n-a-a-vre-pytorch:$1

sudo docker push qcdis/n-a-a-vre:$1
sudo docker push qcdis/n-a-a-vre-laserfarm:$1
sudo docker push qcdis/n-a-a-vre-vol2bird:$1
sudo docker push qcdis/n-a-a-vre-multiply:$1
sudo docker push qcdis/n-a-a-vre-pytorch:$1