FROM qcdis/python-vol2birds:v1.1 AS vol2bird

RUN conda install -c conda-forge conda-pack conda-merge mamba
COPY naa-vre-environment.yaml .

ADD ./jupyterlab_vre-0.1.0-py3-none-any.whl /home/jovyan/jupyterlab_vre-0.1.0-py3-none-any.whl
RUN mamba env update --name venv -f naa-vre-environment.yaml
RUN conda-pack -n venv -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar
RUN /venv/bin/conda-unpack

FROM jupyterhub/k8s-singleuser-sample:1.1.3-n248.h20c9028e

USER root

RUN apt-get update --allow-releaseinfo-change && apt-get -y install fuse

COPY --from=vol2bird /venv /venv

COPY --from=vol2bird /opt/radar/ /opt/radar/
COPY --from=vol2bird /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# set the paths to installed libraries and executables
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/radar/lib:/opt/radar/rave/lib:/opt/radar/rsl/lib:/opt/radar/vol2bird/lib:/usr/lib/x86_64-linux-gnu
ENV PATH=${PATH}:/opt/radar/vol2bird/bin:/opt/radar/rsl/bin

ENV PATH=/venv/bin:$PATH
ENV PATH=/home/jovyan/.local/bin:$PATH
RUN source /venv/bin/activate
RUN echo "source /venv/bin/activate" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

ADD ./start-jupyter.sh /usr/local/bin/start-jupyter.sh
ADD ./start-jupyter-venv.sh /usr/local/bin/start-jupyter-venv.sh
COPY ./repo_utils /tmp/repo_utils

COPY .condarc /tmp/.condarc

COPY init_script.sh /tmp
RUN chown $NB_USER -R /tmp/init_script.sh
RUN chmod ugo+x /tmp/init_script.sh

RUN chmod ugo+x /usr/local/bin/start-jupyter.sh
RUN chmod ugo+x /usr/local/bin/start-jupyter-venv.sh
RUN chown $NB_USER -R /venv/

USER $NB_USER
RUN jupyter serverextension enable --py jupyterlab_vre --user
RUN jupyter serverextension enable --py jupyter_videochat --user
RUN jupyter serverextension enable --py jupyterlab_github --user
RUN jupyter nbextension enable --py widgetsnbextension


RUN jupyter lab build --debug;

cmd ["/usr/local/bin/start-jupyter-venv.sh"]