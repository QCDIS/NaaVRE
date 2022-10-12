


export NB_IP=${NB_IP:-0.0.0.0}
export NB_PORT=${NB_PORT:-8888}
export JUPYTER_ENABLE_LAB=true
export KERNEL_USERNAME=${KERNEL_USERNAME:-${NB_USER}}

echo "Kernel user: " ${KERNEL_USERNAME}
echo "JupyterLab ip:" ${NB_IP}
echo "JupyterLab port: " ${NB_PORT}
echo "Gateway URL: " ${JUPYTER_GATEWAY_URL}

echo "${@: -1}"

exec /usr/local/bin/start-notebook.sh --port=${NB_PORT} --ip=${NB_IP}  $*