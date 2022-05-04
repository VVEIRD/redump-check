#!/bin/bash
filename=$(basename -- "$0")
filename="${filename%.*}"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
c=$(pip list | grep appdirs | wc -l)
if [ ${c} -ne 0 ]; then
    echo Module appdirs is missing, installing
    pip install appdirs
fi
python ${SCRIPT_DIR}/${filename}.py $*
