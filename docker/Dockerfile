FROM jupyterhub/k8s-singleuser-sample:1.1.3-n248.h20c9028e

USER root

ADD start-jupyter.sh /usr/local/bin/start-jupyter.sh
ADD jupyterlab_vre-0.1.0-py3-none-any.whl /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl
COPY ./notebooks/ /home/jovyan/notebooks/

RUN chmod ugo+x /usr/local/bin/start-jupyter.sh

USER $NB_USER

RUN conda remove --force -y terminado && \
    python -m pip install --upgrade pip

RUN python3 -m pip install --quiet --no-cache-dir /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl && \
    jupyter serverextension enable --py jupyterlab_vre --user && \
    jupyter lab build --debug;

#===== Add pdalpy dependencies ======
RUN conda install --yes -c conda-forge pdal python-pdal gdal
RUN conda create --yes -n pdalpy python=3.8
RUN conda activate --yes pdalpy
RUN pip install dask distributed laserfarm
RUN conda upgrade --yes numpy
RUN conda update --yes -n base conda
#====================================

CMD ["/usr/local/bin/start-jupyter.sh"]