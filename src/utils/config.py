"""
Manage configuration data for the app.
"""
import os
import functools


@functools.lru_cache(maxsize=1)
def get_config():
    config = {
        're_url': os.environ.get('KBASE_SECURE_CONFIG_PARAM_RE_API_URL', 'http://re_api:5000').strip('/'),
        'dev': 'DEVELOPMENT' in os.environ,
        'nworkers': os.environ.get('KBASE_SECURE_CONFIG_PARAM_NWORKERS', 2)
    }
    return config
