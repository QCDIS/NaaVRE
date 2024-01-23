# Dev image, intended to run in Tilt dev environment
#
# Build context must be the NaaVRE project root:
# docker build . --file ./docker/vanilla/dev.Dockerfile -t qcdis/n-a-a-vre

FROM condaforge/mambaforge:23.11.0-0  AS env

RUN conda install -c conda-forge conda-pack mamba
COPY environment.yml .

RUN mamba env update --name venv -f environment.yml
RUN conda-pack -n venv -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar
RUN /venv/bin/conda-unpack


FROM jupyterhub/k8s-singleuser-sample:1.2.0 as jupyter-base
USER root

RUN apt-get update --allow-releaseinfo-change && apt-get -y install fuse

# Copy venv
COPY --from=env --chown=$NB_USER:users /venv/ /venv/
ENV PATH=/venv/bin:$PATH
ENV PATH=/home/jovyan/.local/bin:$PATH
RUN chmod +x /venv/bin/activate
#RUN source /venv/bin/activate
SHELL ["/bin/bash", "-c","/venv/bin/activate"]
RUN echo "source /venv/bin/activate" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]


FROM jupyter-base as node-env

# Install ts dependencies
WORKDIR /live/ts
COPY lerna.json .
COPY package.json .
COPY packages/chart-customs/package.json packages/chart-customs/
COPY packages/components/package.json packages/components/
COPY packages/core/package.json packages/core/
COPY packages/experiment-manager/package.json packages/experiment-manager/
COPY packages/notebook-containerizer/package.json packages/notebook-containerizer/
COPY packages/notebook-search/package.json packages/notebook-search/
COPY packages/vre-menu/package.json packages/vre-menu/
COPY packages/vre-panel/package.json packages/vre-panel/
RUN jlpm


FROM jupyter-base as runtime

USER ${NB_USER}

RUN jupyter serverextension enable --py jupyter_videochat --user
RUN jupyter serverextension enable --py jupyterlab_github --user

COPY --from=node-env --chown=$NB_USER:users /live/ts/ /live/ts/

# Install server extension
WORKDIR /live/py
COPY --chown=$NB_USER:users jupyterlab_vre/ jupyterlab_vre/
COPY --chown=$NB_USER:users jupyter-config/ jupyter-config/
COPY --chown=$NB_USER:users setup.py README.md package.json ./
RUN pip install --no-deps -e .
RUN jupyter serverextension enable --py jupyterlab_vre --user

# Install lab extensions
WORKDIR /live/ts
COPY --chown=$NB_USER:users packages/ packages/
COPY --chown=$NB_USER:users tsconfig-base.json .
RUN extensions="chart-customs core notebook-containerizer notebook-search components experiment-manager vre-panel vre-menu"; \
    for ext in $extensions; do \
      npx lerna run build --scope "@jupyter_vre/$ext"; \
    done
RUN extensions="chart-customs core notebook-containerizer notebook-search components experiment-manager vre-panel vre-menu"; \
    for ext in $extensions; do \
      jupyter labextension link --no-build "packages/$ext"; \
    done
RUN jupyter lab build

# Install entrypoints
COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter.sh /usr/local/bin/start-jupyter.sh
COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter-venv.sh /usr/local/bin/start-jupyter-venv.sh
COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter-venv-dev.sh /usr/local/bin/start-jupyter-venv-dev.sh
COPY --chown=$NB_USER:users --chmod=700 docker/init_script.sh /tmp
COPY --chown=$NB_USER:users docker/repo_utils /tmp/repo_utils
COPY --chown=$NB_USER:users docker/vanilla/.condarc /tmp/.condarc

WORKDIR ${HOME}

CMD ["/usr/local/bin/start-jupyter-venv-dev.sh"]
