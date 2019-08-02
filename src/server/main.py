"""
Main HTTP server entrypoint.
"""
import sanic
from sanic_openapi import doc
import traceback
from uuid import uuid4

from src.utils.config import get_config
from src.utils import re_api

_CONF = get_config()
app = sanic.Sanic()
# app.blueprint(api_v1)

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
    return re_api.query("ncbi_taxon_search_sci_name", params)


@app.route('/')
async def health_check(request):
    """Really basic health check; could be expanded if needed."""
    return sanic.response.json({'status': 'ok'})


@app.route('/rpc', methods=["POST"])
async def handle_rpc(req):
    """Handle a JSON RPC 2.0 request."""
    body = req.json
    handlers = {
        'get_taxon': _get_taxon,
        'get_ancestors': _get_ancestors,
        'get_descendants': _get_descendants,
        'get_siblings': _get_siblings,
        'search_taxa': _search_taxa,
    }
    _id = body.get('id', str(uuid4()))
    if not body.get('method') in handlers:
        raise sanic.exceptions.NotFound(f"Method not found: {body.get('method')}")
    meth = handlers[body['method']]
    (result, err) = meth(body.get('params'))
    resp = {'jsonrpc': '2.0', 'id': _id}
    if result:
        resp['result'] = result
    elif err:
        resp['error'] = err
    return sanic.response.json(resp)


@app.exception(sanic.exceptions.NotFound)
async def page_not_found(request, err):
    """Handle 404 as a json response."""
    return sanic.response.json({'error': '404 Not found'}, status=404)


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
