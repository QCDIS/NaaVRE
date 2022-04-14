#!/bin/sh

pip install sentinelhub --upgrade

mkdir dependencies

git clone https://github.com/JorisTimmermans/Deploy_MULTIPLY.git
cd Deploy_MULTIPLY
conda env create -f environments/environment_multiply_platform.yml
cd ../

git clone https://github.com/JorisTimmermans/atmospheric_correction.git
cd atmospheric_correction
python setup.py develop
cd ../


git clone https://github.com/JorisTimmermans/data-access.git
cd data-access
python setup.py develop
cd ../



