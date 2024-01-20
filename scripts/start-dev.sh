#!/bin/bash

set -ex

poetry install --sync
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000