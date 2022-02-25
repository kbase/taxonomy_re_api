"""
Relation engine API client.
"""
import json
import requests
from src.utils.config import get_config
from src.exceptions import REError

_CONF = get_config()


def query(name, params, tok=None):
    """
    Run a stored query from the RE API.

    Returns (from relation_engine)
    {
        "results": list,        # array of result docs, might be empty
        "count": int,           # num docs
        "has_more": bool,       # whether more results for cursor on server
        "cursor_id": str/None,  # id of temporary cursor on server
        "stats": dict,          # stats
    }

    """
    resp = requests.post(
        _CONF['re_url'] + '/api/v1/query_results',
        params={'stored_query': name},
        data=json.dumps(params),
        headers={'Authorization': tok}
    )
    if not resp.ok:
        raise REError(resp)
    return resp.json()
