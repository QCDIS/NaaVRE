SHELL:=/bin/bash

purge:
	rm -rf build *.egg-info yarn-error.log
	rm -rf node_modules lib dist
	rm -rf $$(find packages -name node_modules -type d -maxdepth 2)
	rm -rf $$(find packages -name dist -type d)
	rm -rf $$(find packages -name lib -type d)
	rm -rf $$(find . -name __pycache__ -type d)
	rm -rf $$(find . -name *.tgz)
	rm -rf $$(find . -name tsconfig.tsbuildinfo)
	rm -rf $$(find . -name *.lock)
	rm -rf $$(find . -name package-lock.json)
	rm -rf $$(find . -name .pytest_cache)
	jlpm cache clean

build-backend: 
	python setup.py bdist_wheel sdist

install-backend: build-backend
	pip install --upgrade --upgrade-strategy only-if-needed  --use-deprecated=legacy-resolver dist/jupyterlab_vre-0.1.0-py3-none-any.whl
	jupyter serverextension enable --py jupyterlab_vre --user

build-frontend: jlpm-install
	npx lerna run build --scope @jupyter_vre/chart-customs
	npx lerna run build --scope @jupyter_vre/core
# 	npx lerna run build --scope @jupyter_vre/notebook-containerizer
# 	npx lerna run build --scope @jupyter_vre/notebook-search
# 	npx lerna run build --scope @jupyter_vre/dataset-search
# 	npx lerna run build --scope @jupyter_vre/components
# 	npx lerna run build --scope @jupyter_vre/experiment-manager
# 	npx lerna run build --scope @jupyter_vre/vre-panel
# 	npx lerna run build --scope @jupyter_vre/vre-menu


build-p: jlpm-install
	npx lerna run build --scope @jupyter_vre/vre-panel

install-p:
	$(call INSTALL_LAB_EXTENSION,vre-panel)

link-p:
	$(call LINK_LAB_EXTENSION,vre-panel)


build-exp: jlpm-install
	npx lerna run build --scope @jupyter_vre/experiment-manager

install-exp:
	$(call INSTALL_LAB_EXTENSION,experiment-manager)

link-exp:
	$(call LINK_LAB_EXTENSION,experiment-manager)

jlpm-install:
	jlpm

install-ui:
# 	$(call INSTALL_LAB_EXTENSION,notebook-search)
# 	$(call INSTALL_LAB_EXTENSION,dataset-search)
	$(call INSTALL_LAB_EXTENSION,core)
# 	$(call INSTALL_LAB_EXTENSION,notebook-containerizer)
# 	$(call INSTALL_LAB_EXTENSION,chart-customs)
# 	$(call INSTALL_LAB_EXTENSION,components)
# 	$(call INSTALL_LAB_EXTENSION,experiment-manager)
# 	$(call INSTALL_LAB_EXTENSION,vre-panel)
# 	$(call INSTALL_LAB_EXTENSION,vre-menu)

link-ui:
# 	$(call LINK_LAB_EXTENSION,notebook-search)
# 	$(call LINK_LAB_EXTENSION,dataset-search)
	$(call LINK_LAB_EXTENSION,core)
# 	$(call LINK_LAB_EXTENSION,notebook-containerizer)
# 	$(call LINK_LAB_EXTENSION,chart-customs)
#  	$(call LINK_LAB_EXTENSION,components)
# 	$(call LINK_LAB_EXTENSION,experiment-manager)
# 	$(call LINK_LAB_EXTENSION,vre-panel)
# 	$(call LINK_LAB_EXTENSION,vre-menu)

dist-ui: build-frontend
	mkdir -p dist
	$(call PACKAGE_LAB_EXTENSION,core)
# 	$(call PACKAGE_LAB_EXTENSION,notebook-containerizer)
	$(call PACKAGE_LAB_EXTENSION,chart-customs)
# 	$(call PACKAGE_LAB_EXTENSION,components)
# 	$(call PACKAGE_LAB_EXTENSION,experiment-manager)
# 	$(call PACKAGE_LAB_EXTENSION,vre-panel)
# 	$(call PACKAGE_LAB_EXTENSION,vre-menu)
# 	$(call PACKAGE_LAB_EXTENSION,notebook-search)
# 	$(call PACKAGE_LAB_EXTENSION,dataset-search)

release: dist-ui build-backend
	

define UNLINK_LAB_EXTENSION
	- jupyter labextension unlink --no-build $1
endef

define LINK_LAB_EXTENSION
	cd packages/$1 && jupyter labextension link --no-build .
endef

define UNINSTALL_LAB_EXTENSION
	- jupyter labextension uninstall --no-build $1
endef

define INSTALL_LAB_EXTENSION
	cd packages/$1 && jupyter labextension install --no-build .
endef

define PACKAGE_LAB_EXTENSION
	export PATH=$$(pwd)/node_modules/.bin:$$PATH && cd packages/$1 && npm run dist && mv *.tgz ../../dist
endef