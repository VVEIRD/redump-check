#!/bin/bash
filename=$(basename -- "$0")
filename="${filename%.*}"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python ${SCRIPT_DIR}/${filename}.py $*
