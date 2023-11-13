#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

sh -c /tmp/init_script.sh

source /venv/bin/activate
set -e

# set default ip to 0.0.0.0
if [[ "${NOTEBOOK_ARGS} $*" != *"--ip="* ]]; then
    NOTEBOOK_ARGS="--ip=0.0.0.0 ${NOTEBOOK_ARGS}"
fi

# shellcheck disable=SC1091,SC2086
. /usr/local/bin/start.sh jupyter lab --watch --autoreload ${NOTEBOOK_ARGS} "$@"

