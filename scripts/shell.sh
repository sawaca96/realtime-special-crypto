#!/bin/bash

set -ex

docker compose build
docker compose run --rm app /bin/bash