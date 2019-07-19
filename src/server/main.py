"""
Main HTTP server entrypoint.
"""
import sanic
from sanic_openapi import doc
import traceback

from src.utils.config import get_config
# from src.server.api_versions import api_v1

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


@app.route('/')
async def health_check(request):
    """Really basic health check; could be expanded if needed."""
    return sanic.response.json({'status': 'ok'})


@app.get('/taxa/<taxon_id:int>')
@doc.summary("Fetch a taxon by taxon_id")
@doc.produces(taxon_doc)
async def json_rpc(request, taxon_id):
    """Handle json rpc requests."""
    return sanic.response.json({'taxon_id': taxon_id})


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
