#!/bin/sh
# set -e

PYTHONPATH=/kb/module

# Run linters
flake8 /kb/module/src
mypy --ignore-missing-imports /kb/module/src
bandit -r /kb/module/src

# Run the server and fork
sh /kb/module/src/scripts/entrypoint.sh &

# Wait for the API to start successfully
python -m src.utils.wait_for_services &&

# Run all tests
python -m unittest discover /kb/module/src/test/local_integration
