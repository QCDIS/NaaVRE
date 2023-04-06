#!/bin/sh

mkdir -p $HOME/NaaVRE
cp -r /tmp/repo_utils/conf_vl_repos.py $HOME/NaaVRE/
gitpuller https://github.com/QCDIS/lifewatch-notebooks main example_notebooks
rm -f -- $HOME/NaaVRE/module_name_mapping.json

DIR=$HOME/.multiply/

if [ -d "$DIR" ];
then
    echo "$DIR exists. skipping"
else
  wget $MULTIPLY_CONF_URL -O /tmp/multiply.zip
  unzip /tmp/multiply.zip -d ~/.multiply
fi

python /tmp/repo_utils/conf_vl_repos.py --force=False
