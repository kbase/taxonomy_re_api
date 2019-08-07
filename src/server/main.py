"""
Main HTTP server entrypoint.
"""
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

id_pattern = r'^ncbi_taxon\/\d+$'
# Reusable schema that has an ncbi_taxon id property
id_schema = {
    'type': 'object',
    'required': ['id'],
    'properties': {
        'id': {
            'type': 'string',
            'pattern': id_pattern
        }
    }
}


def _get_taxon(params):
    """
    Fetch a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    jsonschema.validate(instance=params, schema=id_schema)
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_fetch_taxon", {'key': key})


def _get_ancestors(params):
    """
    Fetch ancestor lineage for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    jsonschema.validate(instance=params, schema=id_schema)
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_taxon_get_ancestors", {'key': key})


def _get_descendants(params):
    """
    Fetch the descendants for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = dict(id_schema)  # dict clone
    schema['properties']['levels'] = {'type': 'integer'}  # type: ignore
    jsonschema.validate(instance=params, schema=schema)
    _id = params['id']
    (coll, key) = _id.split('/')
    query = {'key': key}
    if params.get('levels'):
        query['levels'] = params['levels']
    return re_api.query("ncbi_taxon_get_descendants", query)


def _get_siblings(params):
    """
    Fetch the siblings for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    jsonschema.validate(instance=params, schema=id_schema)
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_taxon_get_siblings", {'key': key})


def _search_taxa(params):
    """
    Search for a taxon vertex by scientific name.
    Returns (result, err), one of which will be None.
    """
    schema = {
        'type': 'object',
        'required': ['search_text'],
        'params': {
            'search_text': {'type': 'string'},
            'limit': {'type': 'integer'},
            'offset': {'type': 'integer'}
        }
    }
    jsonschema.validate(instance=params, schema=schema)
    page = params.get('page', 1) - 1
    page_len = params.get('page_len', 20)
    offset = page * 20
    if page_len > 1000:
        raise InvalidParams('Page length is larger than 1000')
    query = {
        'search_text': params['search_text'],
        'limit': page_len,
        'offset': offset
    }
    return re_api.query("ncbi_taxon_search_sci_name", query)


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
        'taxonomy_re_api.get_ancestors': _get_ancestors,
        'taxonomy_re_api.get_descendants': _get_descendants,
        'taxonomy_re_api.get_siblings': _get_siblings,
        'taxonomy_re_api.search_taxa': _search_taxa,
    }
    if not body or not body.get('method'):
        raise InvalidParams("Missing method name")
    if not body.get('method') in handlers:
        raise sanic.exceptions.NotFound(f"Method not found: {body.get('method')}")
    meth = handlers[body['method']]
    params = body.get('params')
    if not isinstance(params, list) or not params:
        raise InvalidParams(f"Method params should be a single-element array. It is: {params}")
    result = meth(params[0])
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
            'error': req.resp_json or req.resp_text,
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


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # nosec
        port=5000,
        debug=_CONF['dev'],
        workers=_CONF['nworkers']
    )
