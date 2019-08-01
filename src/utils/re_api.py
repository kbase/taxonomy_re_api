"""
Relation engine API client.
"""
import json
import requests
from src.utils.config import get_config

_CONF = get_config()


def query(name, params):
    """Run a stored query from the RE API."""
    resp = requests.post(
        _CONF['re_url'] + '/api/v1/query_results',
        params={'stored_query': name},
        data=json.dumps(params)
    )
    body = resp.json()
    if not resp.ok:
        return (None, body['error'])
    return (body, None)
