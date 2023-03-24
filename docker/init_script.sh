#!/bin/sh

mkdir -p /home/jovyan/NaaVRE
cp -r /tmp/repo_utils/conf_vl_repos.py /home/jovyan/NaaVRE/
gitpuller https://github.com/QCDIS/lifewatch-notebooks main example_notebooks
rm -f -- /home/jovyan/NaaVRE/module_name_mapping.json
rm -rf ~/.conda/environments.txt
wget https://github.com/QCDIS/data-access/raw/master/multiply.zip -O /tmp
unzip multiply.zip