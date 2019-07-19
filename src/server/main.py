"""
Main HTTP server entrypoint.
"""
import sanic
import traceback

from src.utils.config import get_config
# from src.server.api_versions import api_v1

_CONF = get_config()
app = sanic.Sanic()
# app.blueprint(api_v1)


@app.route('/')
async def health_check(request):
    """Really basic health check; could be expanded if needed."""
    return sanic.response.json({'status': 'ok'})


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
        host='0.0.0.0',
        port=5000,
        debug=_CONF['dev'],
        workers=_CONF['nworkers']
    )
