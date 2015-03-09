#!/bin/bash -e

source "$(dirname "${BASH_SOURCE[0]}")/project.env"

if [ "x$@" == "x" ]; then
    ARGS=( "tests" "subscriber_server" )
else
    ARGS=$@
fi

cd "${PROJECT_DIR}"
exec python -m pylint --rcfile="${BIN_DIR}/pylint.rc" "${ARGS[@]}"