

RUN git clone https://github.com/JorisTimmermans/Deploy_MULTIPLY.git
WORKDIR Deploy_MULTIPLY
RUN conda env create -f environments/environment_multiply_platform.yml
SHELL ["conda", "run", "-n", "multiply-platform", "/bin/bash", "-c"]