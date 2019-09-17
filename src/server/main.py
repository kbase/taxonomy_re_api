"""
Main HTTP server entrypoint.
"""
import time
import sanic
import jsonschema
import traceback
from jsonschema.exceptions import ValidationError

from src.utils.config import get_config
from src.utils import re_api
from src.exceptions import InvalidParams, REError

_CONF = get_config()
app = sanic.Sanic()
app.config.API_VERSION = '0.1'
app.config.API_TITLE = 'Taxonomy RE API'
app.config.API_DESCRIPTION = 'Taxonomy data API using the relation engine.'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']

# regex pattern for taxon ids
id_pattern = r'^ncbi_taxon\/\d+$'


def _get_taxon(params, headers):
    """
    Fetch a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['id'],
        'properties': {
            'id': {'type': 'string', 'pattern': id_pattern},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    _id = _get_id(params['id'])
    params['id'] = _id
    params['ts'] = params.get('ts', int(time.time() * 1000))
    return re_api.query("ncbi_fetch_taxon", params)


def _get_lineage(params, headers):
    """
    Fetch ancestor lineage for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['id'],
        'properties': {
            'id': {'type': 'string', 'pattern': id_pattern},
            'limit': {'type': 'integer', 'maximum': 1000},
            'offset': {'type': 'integer', 'maximum': 100000},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    params['id'] = _get_id(params['id'])
    params['ts'] = params.get('ts', int(time.time() * 1000))
    results = re_api.query("ncbi_taxon_get_lineage", params)
    return {'stats': results['stats'], 'results': results['results']}


def _get_children(params, headers):
    """
    Fetch the descendants for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['id'],
        'properties': {
            'id': {'type': 'string', 'pattern': id_pattern},
            'limit': {'type': 'integer', 'maximum': 1000},
            'offset': {'type': 'integer', 'maximum': 100000},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    params['id'] = _get_id(params['id'])
    params['ts'] = params.get('ts', int(time.time() * 1000))
    results = re_api.query("ncbi_taxon_get_children", params)
    res = results['results'][0]
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results']}


def _get_siblings(params, headers):
    """
    Fetch the siblings for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['id'],
        'properties': {
            'id': {'type': 'string', 'pattern': id_pattern},
            'limit': {'type': 'integer', 'maximum': 1000},
            'offset': {'type': 'integer', 'maximum': 100000},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    params['id'] = _get_id(params['id'])
    params['ts'] = params.get('ts', int(time.time() * 1000))
    results = re_api.query("ncbi_taxon_get_siblings", params)
    res = results['results'][0]
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results']}


def _search_taxa(params, headers):
    """
    Search for a taxon vertex by scientific name.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['search_text'],
        'params': {
            'search_text': {'type': 'string'},
            'limit': {'type': 'integer', 'maximum': 1000},
            'offset': {'type': 'integer', 'maximum': 100000},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    params['ts'] = params.get('ts', int(time.time() * 1000))
    results = re_api.query("ncbi_taxon_search_sci_name", params)
    res = results['results'][0]
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results']}


def _get_associated_ws_objects(params, headers):
    """
    Get any versioned workspace objects associated with a taxon.
    """
    schema = {
        'type': 'object',
        'required': ['taxon_id'],
        'params': {
            'taxon_id': {'type': 'string', 'pattern': id_pattern},
            'limit': {'type': 'integer', 'maximum': 1000},
            'offset': {'type': 'integer', 'maximum': 100000},
            'ts': {'type': 'integer', 'minimum': 0},
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    params['taxon_id'] = _get_id(params['taxon_id'])
    params['ts'] = params.get('ts', int(time.time() * 1000))
    results = re_api.query("ncbi_taxon_get_associated_ws_objects", params, headers.get('Authorization'))
    return {'stats': results['stats'], 'results': results['results']}


@app.route('/', methods=["POST", "GET", "OPTIONS"])
async def handle_rpc(req):
    """Handle a JSON RPC 1.1 request."""
    if req.method == 'OPTIONS':
        return sanic.response.raw(b'', status=204)
    if req.method == 'GET':
        # Server status request
        return _rpc_resp(req, {'result': [{'status': 'ok'}]})
    body = req.json
    handlers = {
        'taxonomy_re_api.get_taxon': _get_taxon,
        'taxonomy_re_api.get_lineage': _get_lineage,
        'taxonomy_re_api.get_children': _get_children,
        'taxonomy_re_api.get_siblings': _get_siblings,
        'taxonomy_re_api.search_taxa': _search_taxa,
        'taxonomy_re_api.get_associated_ws_objects': _get_associated_ws_objects,
    }
    if not body or not body.get('method'):
        raise InvalidParams("Missing method name")
    if not body.get('method') in handlers:
        raise sanic.exceptions.NotFound(f"Method not found: {body.get('method')}")
    meth = handlers[body['method']]
    params = body.get('params')
    if not isinstance(params, list) or not params:
        raise InvalidParams(f"Method params should be a single-element array. It is: {params}")
    result = meth(params[0], req.headers)
    resp = {'result': [result]}
    return _rpc_resp(req, resp)


@app.middleware('response')
async def cors_resp(req, res):
    """Handle cors response headers."""
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = '*'


@app.exception(sanic.exceptions.NotFound)
async def page_not_found(req, err):
    """Handle 404 as a json response."""
    resp = {
        'error': {
            'name': 'not_found',
            'code': 404,
            'message': 'Not found - ' + str(err),
        }
    }
    return _rpc_resp(req, resp, status=404)


@app.exception(ValidationError)
async def invalid_schema(req, err):
    """Handle a JSON Schema validation error."""
    error = {
        'validator': err.validator,
        'validator_value': err.validator_value,
        'path': err.path,
    }
    resp = {
        'error': {
            'name': 'params_invalid',
            'error': error,
            'code': 400,
            'message': 'Parameter validation error: ' + err.message,
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(REError)
async def re_api_error(req, err):
    resp = {
        'error': {
            'name': 'relation_engine_error',
            'code': 400,
            'message': 'Relation engine API error',
            'error': err.resp_json or err.resp_text,
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(sanic.exceptions.InvalidUsage)
async def invalid_usage(req, err):
    resp = {
        'error': {
            'name': 'invalid_usage',
            'message': str(err),
            'code': 400,
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(InvalidParams)
async def invalid_params(req, err):
    resp = {
        'error': {
            'name': 'invalid_request',
            'message': str(err),
            'code': 400,
        }
    }
    return _rpc_resp(req, resp, status=400)


# Any other exception -> 500
@app.exception(Exception)
async def server_error(req, err):
    traceback.print_exc()
    error = {'class': err.__class__.__name__}
    resp = {
        'error': {
            'name': 'uncaught_error',
            'code': 500,
            'message': str(err),
            'error': error
        }
    }
    return _rpc_resp(req, resp, status=500)


def _rpc_resp(req, resp, status=200):
    resp['version'] = '1.1'
    if req.json and req.json.get('id'):
        resp['id'] = req.json['id']
    return sanic.response.json(resp, status)


def _get_id(param_id):
    """Get the document id portion of the ID parameter."""
    (coll, _id) = param_id.split('/')
    return _id


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # nosec
        port=5000,
        debug=_CONF['dev'],
        workers=_CONF['nworkers']
    )
