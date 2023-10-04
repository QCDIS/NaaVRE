# Dev image, intended to run in Tilt dev environment
#
# Build context must be the NaaVRE project root:
# docker build . --file ./docker/vanilla/dev.Dockerfile -t qcdis/n-a-a-vre

FROM condaforge/mambaforge:23.1.0-2  AS env

RUN conda install -c conda-forge conda-pack mamba
COPY environment.yml .

RUN mamba env update --name venv -f environment.yml
RUN conda-pack -n venv -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar
RUN /venv/bin/conda-unpack

FROM condaforge/mambaforge:23.1.0-2 as builder

COPY --from=env /venv/ /venv/

WORKDIR /build

COPY Makefile .
COPY setup.py .
COPY README.md .
COPY package.json .
COPY jupyter-config/ ./jupyter-config/
COPY jupyterlab_vre/ ./jupyterlab_vre/
RUN python setup.py bdist_wheel sdist


FROM jupyterhub/k8s-singleuser-sample:1.1.3-n248.h20c9028e AS runtime
USER root

RUN apt-get update --allow-releaseinfo-change && apt-get -y install fuse

COPY --from=env --chown=$NB_USER:users /venv/ /venv/

ENV PATH=/venv/bin:$PATH
ENV PATH=/home/jovyan/.local/bin:$PATH
RUN source /venv/bin/activate
RUN echo "source /venv/bin/activate" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# Install jupyterlab_vre without dependency resolution; they were installed at the env step
COPY --from=builder --chown=$NB_USER:users /build/dist/jupyterlab_vre-0.1.0-py3-none-any.whl .
RUN pip install --no-deps ./jupyterlab_vre-0.1.0-py3-none-any.whl

USER $NB_USER
RUN jupyter serverextension enable --py jupyterlab_vre --user
RUN jupyter serverextension enable --py jupyter_videochat --user
RUN jupyter serverextension enable --py jupyterlab_github --user

RUN jupyter lab build --debug

COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter.sh /usr/local/bin/start-jupyter.sh
COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter-venv.sh /usr/local/bin/start-jupyter-venv.sh
COPY --chown=$NB_USER:users --chmod=700 docker/start-jupyter-venv-dev.sh /usr/local/bin/start-jupyter-venv-dev.sh
COPY --chown=$NB_USER:users --chmod=700 docker/init_script.sh /tmp
COPY --chown=$NB_USER:users docker/repo_utils /tmp/repo_utils
COPY --chown=$NB_USER:users docker/vanilla/.condarc /tmp/.condarc

CMD ["/usr/local/bin/start-jupyter-venv-dev.sh"]
