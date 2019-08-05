"""
Main HTTP server entrypoint.
"""
import sanic
from sanic_cors import CORS
from sanic_openapi import doc
import traceback
from uuid import uuid4

from src.utils.config import get_config
from src.utils import re_api
from src.exceptions import InvalidParams

_CONF = get_config()
app = sanic.Sanic()
CORS(app, automatic_options=True)

app.config.API_VERSION = '0.1'
app.config.API_TITLE = 'Taxonomy RE API'
app.config.API_DESCRIPTION = 'Taxonomy data API using the relation engine.'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']

taxon_doc = doc.JsonBody({
    '_key': doc.String,
    'scientific_name': doc.String,
    'canonical_scientific_name': [doc.String],
    'cars': [{
        'category': doc.String,
        'name': doc.String,
        'canonical': [doc.String]
    }],
    'rank': doc.String,
    'numeric_rank': doc.String,
    'NCBI_taxon_id': doc.Integer,
    'genetic_code': doc.Integer
})


def _get_taxon(params):
    """
    Fetch a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_fetch_taxon", {'key': key})


def _get_ancestors(params):
    """
    Fetch ancestor lineage for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_taxon_get_ancestors", {'key': key})


def _get_descendants(params):
    """
    Fetch the descendants for a taxon by ID.
    Returns (result, err), one of which will be None.
    """
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
    _id = params['id']
    (coll, key) = _id.split('/')
    return re_api.query("ncbi_taxon_get_siblings", {'key': key})


def _search_taxa(params):
    """
    Search for a taxon vertex by scientific name.
    Returns (result, err), one of which will be None.
    """
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


@app.route('/', methods=["POST", "GET"])
async def handle_rpc(req):
    """Handle a JSON RPC 1.1 request."""
    if req.method == 'GET':
        # Server status request
        return sanic.response.json({'status': 'ok'})
    body = req.json
    handlers = {
        'taxonomy_re_api.get_taxon': _get_taxon,
        'taxonomy_re_api.get_ancestors': _get_ancestors,
        'taxonomy_re_api.get_descendants': _get_descendants,
        'taxonomy_re_api.get_siblings': _get_siblings,
        'taxonomy_re_api.search_taxa': _search_taxa,
    }
    _id = body.get('id', str(uuid4()))
    if not body.get('method') in handlers:
        raise sanic.exceptions.NotFound(f"Method not found: {body.get('method')}")
    meth = handlers[body['method']]
    params = body.get('params')
    if not isinstance(params, list) or not params:
        raise InvalidParams(f"Method params should be a single-element array: {params}")
    (result, err) = meth(params[0])
    resp = {'version': '2.0', 'id': _id}
    if result:
        resp['result'] = [result]
    elif err:
        resp['error'] = err
    return sanic.response.json(resp)


@app.exception(sanic.exceptions.NotFound)
async def page_not_found(request, err):
    """Handle 404 as a json response."""
    return sanic.response.json({'error': '404 Not found'}, status=404)


@app.exception(InvalidParams)
async def invalid_params(request, err):
    resp = {'error': str(err), 'type': 'invalid_params'}
    return sanic.response.json(resp, status=400)


# Any other exception -> 500
@app.exception(Exception)
async def server_error(request, err):
    traceback.print_exc()
    resp = {'error': '500 - Server error'}
    if _CONF['dev']:
        resp['error_class'] = err.__class__.__name__
        resp['error_details'] = str(err)
    return sanic.response.json(resp, status=500)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # nosec
        port=5000,
        debug=_CONF['dev'],
        workers=_CONF['nworkers']
    )
