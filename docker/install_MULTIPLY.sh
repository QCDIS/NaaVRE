#!/bin/sh

mkdir dependencies
cd dependencies

#
pip install sentinelhub --upgrade

git clone https://github.com/JorisTimmermans/atmospheric_correction.git
cd atmospheric_correction
python setup.py develop
cd ../


git clone https://github.com/JorisTimmermans/BRDF_descriptors.git
BRDF_descriptors
python setup.py install
cd ../

git clone https://github.com/JorisTimmermans/data-access.git
cd data-access
python setup.py develop
cd ../


git clone https://github.com/multiply-org/inference-engine.git
cd inference-engine
python setup.py develop
cd ../

git clone https://github.com/JorisTimmermans/multiply-core.git
cd multiply-core
python setup.py develop
cd ../

git clone https://github.com/multiply-org/KaFKA-InferenceEngine.git
cd KaFKA-InferenceEngine
python setup.py develop
cd ../

git clone https://github.com/multiply-org/sar-pre-processing.git
cd sar-pre-processing
python setup.py develop
cd ../

git clone https://github.com/JorisTimmermans/vm-support.git
cd vm-support
python setup.py develop
cd ../

