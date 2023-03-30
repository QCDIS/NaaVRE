#!/bin/sh

mkdir -p /home/jovyan/NaaVRE
cp -r /tmp/repo_utils/conf_vl_repos.py /home/jovyan/NaaVRE/
gitpuller https://github.com/QCDIS/lifewatch-notebooks main example_notebooks
rm -f -- /home/jovyan/NaaVRE/module_name_mapping.json

DIR=/home/jovyan/.multiply/

if [ -d "$DIR" ];
then
    echo "$DIR exists. skipping"
else
  wget $MULTIPLY_CONF_URL -O /tmp/multiply.zip
  unzip /tmp/multiply.zip -d ~/.multiply
fi

python /tmp/repo_utils/conf_vl_repos.py --force=False --github_url=$CELL_GITHUB --github_token=$CELL_GITHUB_TOKEN --registry_url=$REGISTRY_URL
