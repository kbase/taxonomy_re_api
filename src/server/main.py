"""
Main HTTP server entrypoint.
"""
import time
import sanic
import jsonschema
import traceback
from jsonschema.exceptions import ValidationError
from contextlib import suppress

from src.utils.config import get_config
from src.utils.schemas import load_schemas
from src.utils.search import clean_search_text
from src.utils import re_api
from src.exceptions import MethodNotFound, InvalidRequest, InvalidParams, ServerError, REError

_CONF = get_config()
_SCHEMAS = load_schemas()
app = sanic.Sanic(name='Taxonomy RE API')
app.config.API_TITLE = 'Taxonomy RE API'
app.config.API_DESCRIPTION = 'Taxonomy data API using the relation engine.'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']


def transform_taxon_results(taxa, ns, ns_config):
    """
    Make some modifications on any taxon results given a namespace config (see _NS_CONFIG)
    Mutates each dict in the given `taxa` list
    """
    for taxon in taxa:
        taxon['ns'] = ns


def transform_query_params(params, required_ns_fields=[], field_name_remappings={}):
    """
    Set some defaults in the params that we pass into an RE query.
    `field_name_remappings` can be a dict of {'input_param_field_name': 'field_name_to_send_to_query'}
    Mutates the params dict
    Returns the namespace name and the namespace config dict as a pair (see _NS_CONFIG below)
    """
    ns = params.pop('ns')
    ns_config = _NS_CONFIG[ns]
    for field_name in required_ns_fields:
        params[field_name] = ns_config['query_params'][field_name]
    for (input_name, output_name) in field_name_remappings.items():
        params[output_name] = params.pop(input_name)
    params.setdefault('ts', int(time.time() * 1000))
    return (ns, ns_config)


# Mapping of namespace names to collection and field names
# The 'translate_field_name' options are used to change field names in the source document.
_NS_CONFIG = {
    'ncbi_taxonomy': {
        'query_params': {
            '@taxon_coll': 'ncbi_taxon',
            '@taxon_child_of': 'ncbi_child_of_taxon',
            'sciname_field': 'scientific_name',
        },
    },
    'gtdb': {
        'query_params': {
            '@taxon_coll': 'gtdb_taxon',
            '@taxon_child_of': 'gtdb_child_of_taxon',
            'sciname_field': 'scientific_name',
        },
    },
    'rdp_taxonomy': {
        'query_params': {
            '@taxon_coll': 'rdp_taxon',
            '@taxon_child_of': 'rdp_child_of_taxon',
            'sciname_field': 'name',
        }
    },
    'silva_taxonomy': {
        'query_params': {
            '@taxon_coll': 'silva_taxon',
            '@taxon_child_of': 'silva_child_of_taxon',
            'sciname_field': 'name',
        }
    }
}


def _get_taxon(params, headers):
    """
    Fetch a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = _SCHEMAS['get_taxon']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll',))
    results = re_api.query("taxonomy_fetch_taxon", params)
    transform_taxon_results(results['results'], ns, ns_config)
    return {'stats': results['stats'], 'results': results['results'], 'ts': params['ts']}


def _get_taxon_from_ws_obj(params, headers):
    """
    Fetch the taxon document from a workspace object reference.
    """
    schema = _SCHEMAS['get_taxon_from_ws_obj']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll',))
    params['obj_ref'] = params['obj_ref'].replace('/', ':')
    results = re_api.query("taxonomy_get_taxon_from_ws_obj", params)
    transform_taxon_results(results['results'], ns, ns_config)
    return {'stats': results['stats'], 'results': results['results'], 'ts': params['ts']}


def _get_lineage(params, headers):
    """
    Fetch ancestor lineage for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = _SCHEMAS['get_lineage']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll', '@taxon_child_of'))
    results = re_api.query("taxonomy_get_lineage", params)
    transform_taxon_results(results['results'], ns, ns_config)
    return {'stats': results['stats'], 'results': results['results'], 'ts': params['ts']}


def _get_children(params, headers):
    """
    Fetch the descendants for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = _SCHEMAS['get_children']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll', '@taxon_child_of', 'sciname_field'))
    results = re_api.query("taxonomy_get_children", params)
    res = results['results'][0]
    transform_taxon_results(res['results'], ns, ns_config)
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results'], 'ts': params['ts']}


def _get_siblings(params, headers):
    """
    Fetch the siblings for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    schema = _SCHEMAS['get_siblings']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll', '@taxon_child_of', 'sciname_field'))
    results = re_api.query("taxonomy_get_siblings", params)
    res = results['results'][0]
    transform_taxon_results(res['results'], ns, ns_config)
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results'], 'ts': params['ts']}


def _search_taxa(params, headers):
    """
    Search for a taxon vertex by scientific name.
    Returns (result, err), one of which will be None.
    """
    schema = _SCHEMAS['search_taxa']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll', 'sciname_field'))
    results = re_api.query("taxonomy_search_sci_name", params)
    res = results['results'][0]
    transform_taxon_results(res['results'], ns, ns_config)
    return {
        'stats': results['stats'],
        'total_count': res.get('total_count'),
        'results': res['results'],
        'ts': params['ts']
    }


def _search_species(params, headers):
    """
    Search for a species or strain.

    Schema params are:
    * search_text (required)
    * ns (required)
    * ts
    * limit
    * offset
    * select

    Response looks like:
    {
        "results": [...],   # docs
        "count": ...,       # num docs
        "has_more": ...,
        "cursor_id": ...,
        "stats": {...},
    }
    """
    schema = _SCHEMAS['search_species']
    jsonschema.validate(instance=params, schema=schema)
    ns, ns_config = transform_query_params(
        params=params,
        required_ns_fields=('@taxon_coll', 'sciname_field'),
    )
    # Check if the search text is acceptable for AQL
    params['search_text'] = clean_search_text(params['search_text'])
    if params['search_text']:
        stored_query = (
            'taxonomy_search_species_strain_no_sort'
            if len(params['search_text']) <= 3
            else 'taxonomy_search_species_strain'
        )
        resp_json = re_api.query(stored_query, params)
        transform_taxon_results(resp_json['results'], ns, ns_config)
        return {
            'results': resp_json['results'],
            'ts': params['ts'],
            'stats': resp_json['stats'],
        }
    else:
        return {
            'results': [],
            'ts': params['ts'],
            'stats': None,
        }


def _get_associated_ws_objects(params, headers):
    """
    Get any versioned workspace objects associated with a taxon.
    """
    schema = _SCHEMAS['get_associated_ws_objects']
    jsonschema.validate(instance=params, schema=schema)
    (ns, ns_config) = transform_query_params(params, ('@taxon_coll',), {'id': 'taxon_id'})
    results = re_api.query("taxonomy_get_associated_ws_objects", params, headers.get('Authorization'))
    res = results['results'][0]
    transform_taxon_results(results['results'], ns, ns_config)
    for res in results['results']:
        # Write some extra metadata about the workspace for each object
        for elem in res['results']:
            obj = elem['ws_obj']
            obj['workspace'] = {
                'refdata_source': obj['ws_info'].get('metadata', {}).get('refdata_source'),
                'narr_name': obj['ws_info'].get('metadata', {}).get('narrative_nice_Name'),
            }
            del obj['ws_info']
    return {'stats': results['stats'], 'total_count': res['total_count'], 'results': res['results']}


def _get_data_sources(params, headers):
    """
    Returns a list of all Taxonomy Sources
    """
    schema = _SCHEMAS['get_data_sources']

    # parameters for get_data_sources are not actually required, as omitting
    # the parameters (which filter the sources) implies returning all.
    if params is not None:
        jsonschema.validate(instance=params, schema=schema)

    re_params = {
        'type': 'taxonomy',
    }

    # Be nice. Filtering by ns can be skipped by either setting 'ns' to null, or
    # omitting it from the params object.
    if params is not None and params.get('ns') is not None:
        re_params['ns'] = params.get('ns')
        response = re_api.query("data_sources_get_data_sources", re_params, headers.get('Authorization'))
    else:
        response = re_api.query("data_sources_get_all_data_sources", re_params, headers.get('Authorization'))

    sources = []
    for source in response['results']:
        del source['_id']
        del source['_key']
        del source['_rev']
        sources.append(source)

    return {
        'sources': sources
    }


def _rpc_resp(req, resp, status=200):
    resp['version'] = '1.1'
    # We need to suppress the call for json
    # since it fails if the request does not
    # have json.
    has_json = False
    with suppress(Exception):
        if req.json:
            has_json = True

    if has_json and 'id' in req.json:
        resp['id'] = req.json['id']

    return sanic.response.json(resp, status)


def get_json_type(json_value):
    if isinstance(json_value, str):
        return 'string'
    elif isinstance(json_value, bool):
        return 'boolean'
    elif isinstance(json_value, int) or isinstance(json_value, float):
        return 'number'
    elif isinstance(json_value, dict):
        return 'object'
    if isinstance(json_value, list):
        return 'array'
    elif json_value is None:
        return 'null'
    else:
        # should be impossible
        raise Exception('Not a json type')


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
        'taxonomy_re_api.search_species': _search_species,
        'taxonomy_re_api.get_associated_ws_objects': _get_associated_ws_objects,
        'taxonomy_re_api.get_taxon_from_ws_obj': _get_taxon_from_ws_obj,
        'taxonomy_re_api.get_data_sources': _get_data_sources,
    }

    # Validate  JSON-RPC 1.1 overall structure

    if not body:
        raise InvalidRequest("Request is not valid")

    if not isinstance(body, dict):
        raise InvalidRequest("Request is not valid")

    # Validate version

    if 'version' not in body:
        raise InvalidRequest("Missing version version in request")

    if body['version'] != '1.1':
        raise InvalidRequest("Version must be 1.1")

    # Validate method

    if 'method' not in body:
        raise InvalidRequest("Missing method name in request")

    method = body['method']

    if not isinstance(method, str):
        raise InvalidRequest("Request method is invalid")

    # Validate params

    if 'params' not in body:
        raise InvalidRequest("Missing params in request")

    params = body['params']

    if not isinstance(params, list):
        raise InvalidRequest(f'Method params should be an array, it is a "{get_json_type(params)}"')

    param = None
    if len(params) == 1:
        param = params[0]
    elif len(params) > 1:
        raise InvalidParams(f"Method params array can only include at most one item, it has {len(params)}")

    # Run the method
    if method not in handlers:
        raise MethodNotFound(method)

    meth = handlers[method]

    result = meth(param, req.headers)
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
        'message': 'Parameter validation error: ' + err.message,
        'validator': err.validator,
        'validator_value': err.validator_value,
        'path': list(err.path),
    }
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': InvalidParams.code,
            'message': 'Invalid params',
            'error': error
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(REError)
async def re_api_error(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': ServerError.code,
            'message': 'Server error',
            'error': {
                'message': 'Relation engine API error',
                're_error': err.resp_json or err.resp_text
            }
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(sanic.exceptions.InvalidUsage)
async def invalid_usage(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': InvalidRequest.code,
            'message': 'Invalid request',
            'error': {
                'message': str(err),
            }

        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(sanic.exceptions.MethodNotSupported)
async def method_not_supported(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': InvalidRequest.code,
            'message': 'Invalid request',
            'error': {
                'message': str(err),
            }
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(InvalidRequest)
async def invalid_request(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': err.code,
            'message': 'Invalid request',
            'error': {
                'message': str(err)
            }
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(MethodNotFound)
async def method_not_found(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': err.code,
            'message': 'Method not found',
            'error': {
                'message': f'Method "{err.method_name}" not found',
                'method': err.method_name
            }
        }
    }
    return _rpc_resp(req, resp, status=400)


@app.exception(InvalidParams)
async def invalid_params(req, err):
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': err.code,
            'message': 'Invalid params',
            'error': {
                'message': str(err),
            }
        }
    }
    return _rpc_resp(req, resp, status=400)


# Any other exception -> 500
@app.exception(Exception)
async def server_error(req, err):
    traceback.print_exc()
    resp = {
        'error': {
            'name': 'JSONRPCError',
            'code': ServerError.code,
            'message': 'Server error',
            'error': {
                'message': str(err),
                'class': err.__class__.__name__
            }
        }
    }
    return _rpc_resp(req, resp, status=500)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # nosec
        port=5000,
        debug=_CONF['dev'],
        workers=_CONF['nworkers']
    )
