#!/bin/sh

mkdir -p $HOME/NaaVRE
cp -r /tmp/repo_utils/conf_vl_repos.py $HOME/NaaVRE/
rm -f -- $HOME/NaaVRE/module_name_mapping.json

DIR=$HOME/.multiply/

if [ -d "$DIR" ];
then
    echo "$DIR exists. skipping"
else
  wget $MULTIPLY_CONF_URL -O /tmp/multiply.zip
  unzip /tmp/multiply.zip -d ~/multiply
  mv multiply/multiply .multiply
  rm -r multiply
fi

python /tmp/repo_utils/conf_vl_repos.py --force=False
