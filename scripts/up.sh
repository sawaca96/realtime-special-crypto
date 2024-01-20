#!/bin/bash

set -ex

ARGS=()
USE_APP_PROFILE=false

while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --app)
        USE_APP_PROFILE=true
        shift
        ;;
        *)
        ARGS+=("$1")
        shift
        ;;
    esac
done

# Remove --app from ARGS if present
ARGS=(${ARGS[@]//--app})

if [ "$USE_APP_PROFILE" = true ]; then    
    docker compose --profile app build 
    docker compose --profile app up "${ARGS[@]}"
else
    docker compose up "${ARGS[@]}"
fi
