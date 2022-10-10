#!/bin/sh

cp dist/jupyterlab_vre-0.1.0-py3-none-any.whl docker/
cd docker

sudo docker build . --file Dockerfile-laserfarm -t qcdis/n-a-a-vre-laserfarm:$1
sudo docker build . --file Dockerfile-vol2bird -t qcdis/n-a-a-vre-vol2bird:$1
sudo docker build . --file Dockerfile-MULTIPLY -t qcdis/n-a-a-vre-multiply:$1
sudo docker build . --file Dockerfile-laserfarm -t qcdis/n-a-a-vre-pytorch:$1

sudo docker push qcdis/n-a-a-vre-laserfarm:"$1"
sudo docker push qcdis/n-a-a-vre-vol2bird:"$1"
sudo docker push qcdis/n-a-a-vre-multiply:"$1"
sudo docker push qcdis/n-a-a-vre-pytorch:"$1"

sudo docker tag qcdis/n-a-a-vre-laserfarm:"$1" qcdis/n-a-a-vre-laserfarm:latest
sudo docker push qcdis/n-a-a-vre-laserfarm:latest

sudo docker tag qcdis/n-a-a-vre-vol2bird:"$1" qcdis/n-a-a-vre-vol2bird:latest
sudo docker push qcdis/n-a-a-vre-vol2bird:latest

sudo docker tag qcdis/n-a-a-vre-multiply:"$1" qcdis/n-a-a-vre-multiply:latest
sudo docker push qcdis/n-a-a-vre-multiply:latest

sudo docker tag qcdis/n-a-a-vre-pytorch:"$1" qcdis/n-a-a-vre-pytorch:latest
sudo docker push qcdis/n-a-a-vre-pytorch:latest

cd ../