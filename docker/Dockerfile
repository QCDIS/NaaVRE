FROM jupyterhub/k8s-singleuser-sample:1.1.3-n248.h20c9028e

USER root

RUN apt-get update --allow-releaseinfo-change && apt-get -y install s3fs git

ADD start-jupyter.sh /usr/local/bin/start-jupyter.sh
ADD jupyterlab_vre-0.1.0-py3-none-any.whl /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl
COPY ./repo_utils/ /tmp/repo_utils

RUN chmod ugo+x /usr/local/bin/start-jupyter.sh

USER $NB_USER

RUN conda remove --force -y terminado && \
    python -m pip install --upgrade pip

RUN python3 -m pip install --quiet --no-cache-dir /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl && \
    jupyter serverextension enable --py jupyterlab_vre --user

RUN pip install jupyterlab-github jupyter-videochat nbgitpuller jupyterlab-lsp python-lsp-server[all] pre-commit ggshield && \
    jupyter serverextension enable --py jupyter_videochat --user && \
    jupyter serverextension enable --py jupyterlab_github --user

RUN jupyter lab build --debug;
RUN conda clean -a -y
CMD ["/usr/local/bin/start-jupyter.sh"]