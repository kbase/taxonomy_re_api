import requests
from src.test.test_base import TestBase, api_url, verify_ssl


class TestJSONRPC(TestBase):

    # Tests for JSON-RPC 1.1

    def test_invalid_http_method(self):
        resp = requests.delete(api_url(), verify=verify_ssl())
        self.assertFalse(resp.ok, resp.text)
        self.assertTrue('error' in resp.json())

    def test_invalid_params_type_string(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': 'xyz!'
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "string"'
        })

    def test_invalid_params_type_boolean(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': True
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "boolean"'
        })

    def test_invalid_params_type_number1(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': 123
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "number"'
        })

    def test_invalid_params_type_number2(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': 123.456
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "number"'
        })

    def test_invalid_params_type_null(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': None
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "null"'
        })

    def test_invalid_params_type_object(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': {}
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Method params should be an array, it is a "object"'
        })

    def test_missing_method(self):
        resp = self.request({
            'version': '1.1',
            'params': []
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Missing method name in request'
        })

    def test_invalid_method_type(self):
        resp = self.request({
            'version': '1.1',
            'method': None,
            'params': []
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Request method is invalid'
        })

    def test_unknown_method(self):
        resp = self.request({
            'version': '1.1',
            'method': 'xyz',
            'params': [],
        })
        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32601, 'Method not found', {
            'message': 'Method "xyz" not found',
            'method': 'xyz'
        })

    def test_missing_params(self):
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_lineage',
        })

        self.assertFalse(resp.ok, resp.text)
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request', {
            'message': 'Missing params in request'
        })
