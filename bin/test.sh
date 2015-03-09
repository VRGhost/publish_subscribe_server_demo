#!/bin/sh -e

source "$(dirname "${BASH_SOURCE[0]}")/project.env"

if [ "x$@" == "x" ]; then
    ARGS=( "tests" )
else
    ARGS=$@
fi


cd "${PROJECT_DIR}"
exec python -m trial "${ARGS[@]}"