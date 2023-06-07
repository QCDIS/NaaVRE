FROM rocker/r-ver:4.1.1
LABEL maintainer="o2r"
# CRAN packages skipped because they are in the base image: dplyr, forcats, ggplot2, knitr, readr
RUN export DEBIAN_FRONTEND=noninteractive; apt-get -y update \
  && apt-get install -y git-core
WORKDIR /payload/
CMD ["R"]