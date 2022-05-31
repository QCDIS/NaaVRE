FROM jupyterhub/k8s-singleuser-sample:1.1.3-n248.h20c9028e

USER root

ADD start-jupyter.sh /usr/local/bin/start-jupyter.sh
ADD jupyterlab_vre-0.1.0-py3-none-any.whl /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl
COPY ./notebooks/ /tmp/notebooks

RUN chmod ugo+x /usr/local/bin/start-jupyter.sh

USER $NB_USER

RUN conda remove --force -y terminado && \
    python -m pip install --upgrade pip

RUN pip install jupyterlab-s3-browser && \
    jupyter serverextension enable --py jupyterlab_s3_browser --user && \
    jupyter lab build --debug;

RUN python3 -m pip install --quiet --no-cache-dir /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl && \
    jupyter serverextension enable --py jupyterlab_vre --user && \
    jupyter lab build --debug;

CMD ["/usr/local/bin/start-jupyter.sh"]