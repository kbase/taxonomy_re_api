"""
Wait for services to start.

To wait on the main app/API:
    python wait_for_services.py app
To wait on dependency services
    python wait_for_services.py
"""
import requests
import time


def wait_for_app():
    """Wait for the app to start."""
    url = 'http://localhost:5000'
    started = False
    timeout = time.time() + 60
    while not started:
        try:
            requests.get(url).raise_for_status()
            started = True
        except Exception:
            if time.time() > timeout:
                raise RuntimeError('Timed out waiting for app to start.')
            time.sleep(3)


if __name__ == '__main__':
    wait_for_app()
