#!/bin/sh -e

source "$(dirname "${BASH_SOURCE[0]}")/project.env"

cd "${PROJECT_DIR}"
exec python -m subscriber_server "$@"