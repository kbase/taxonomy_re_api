"""
Wait for services to start.

To wait on the main app/API:
    python wait_for_services.py app
To wait on dependency services
    python wait_for_services.py
"""
import sys
import requests
import time


def wait_for_deps():
    """Wait for any dependency services to start."""
    # TODO
    started = False
    while not started:
        pass


def wait_for_app():
    """Wait for the API itself to start."""
    # TODO
    started = False
    while not started:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'app':
        wait_for_app()
    else:
        wait_for_deps()
