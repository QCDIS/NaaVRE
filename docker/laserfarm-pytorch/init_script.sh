#!/bin/sh

mkdir -p $HOME/NaaVRE/
mkdir -p /tmp/data
cp -r /tmp/repo_utils/conf_vl_repos.py $HOME/NaaVRE/
rm -f -- $HOME/NaaVRE/module_name_mapping.json
python /tmp/repo_utils/conf_vl_repos.py --force=False
