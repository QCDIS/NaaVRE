#!/bin/sh

cd docker
sudo docker push qcdis/n-a-a-vre:"$1"
sudo docker push qcdis/n-a-a-vre-laserfarm:"$1"
sudo docker push qcdis/n-a-a-vre-vol2bird:"$1"
sudo docker push qcdis/n-a-a-vre-multiply:"$1"
sudo docker push qcdis/n-a-a-vre-pytorch:"$1"

sudo docker tag qcdis/n-a-a-vre:"$1" qcdis/n-a-a-vre:latest
sudo docker push qcdis/n-a-a-vre:latest

sudo docker tag qcdis/n-a-a-vre-laserfarm:"$1" qcdis/n-a-a-vre-laserfarm:latest
sudo docker push qcdis/n-a-a-vre-laserfarm:latest

sudo docker tag qcdis/n-a-a-vre-vol2bird:"$1" qcdis/n-a-a-vre-vol2bird:latest
sudo docker push qcdis/n-a-a-vre-vol2bird:latest

sudo docker tag qcdis/n-a-a-vre-multiply:"$1" qcdis/n-a-a-vre-multiply:latest
sudo docker push qcdis/n-a-a-vre-multiply:latest

sudo docker tag qcdis/n-a-a-vre-pytorch:"$1" qcdis/n-a-a-vre-pytorch:latest
sudo docker push qcdis/n-a-a-vre-pytorch:latest

cd ../