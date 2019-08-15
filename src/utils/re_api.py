"""
Relation engine API client.
"""
import json
import requests
from src.utils.config import get_config
from src.exceptions import REError

_CONF = get_config()


def query(name, params, tok=None):
    """Run a stored query from the RE API."""
    resp = requests.post(
        _CONF['re_url'] + '/api/v1/query_results',
        params={'stored_query': name},
        data=json.dumps(params),
        headers={'Authorization': tok}
    )
    if not resp.ok:
        raise REError(resp)
    return resp.json()
