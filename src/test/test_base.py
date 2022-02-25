import unittest
import os
import requests
import json


def api_url():
    return os.environ.get('API_URL', 'http://localhost:5000')


def verify_ssl():
    return os.environ.get('VERIFY_SSL', 't').lower() not in ['f', 'false', 'n', 'no']


print('Test Settings')
print('-------------')
print(f'API_URL   : {api_url()}')
print(f'VERIFY_SSL: {verify_ssl()}')


TS = 1635479149946  # when test was written


class TestBase(unittest.TestCase):

    # Bundled assertions

    def assert_is_jsonrpc_base(self, rpc_response):
        self.assertIsInstance(rpc_response, dict)
        self.assertIn('version', rpc_response)
        self.assertEqual(rpc_response.get('version'), '1.1')

    def assert_is_error_response(self, rpc_response, code, message, error=None):
        self.assert_is_jsonrpc_base(rpc_response)
        self.assertIn('error', rpc_response)
        rpc_error = rpc_response['error']
        self.assertIsInstance(rpc_error, dict)
        self.assertIsInstance(rpc_error.get('message'), str)
        self.assertEqual(rpc_error.get('code'), code)
        self.assertEqual(rpc_error.get('name'), 'JSONRPCError')
        self.assertEqual(rpc_error.get('message'), message)

        # Test any error detail
        if error is not None:
            self.assertIn('error', rpc_error)
            if 'error' in rpc_error:
                self.assertIsInstance(rpc_error['error'], dict)
                for key, value in error.items():
                    self.assertEqual(rpc_error['error'].get(key), value)
        return error

    def assert_is_result_response(self, rpc_response):
        self.assert_is_jsonrpc_base(rpc_response)
        self.assertIn('result', rpc_response)
        result = rpc_response['result']
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        return result[0]

    def assert_query_results(
        self,
        sciname_target,
        search_text_exp_hit,
        search_text_exp_miss=[],
        expired=False,
    ):
        ts_params = {'ts': None} if expired else {}
        for st in search_text_exp_hit + search_text_exp_miss:
            resp = self.request({
                'version': '1.1',
                'method': 'taxonomy_re_api.search_species',
                'params': [{
                    'search_text': st,
                    'ns': 'ncbi_taxonomy',
                    **ts_params,
                }]
            })
            self.assertTrue(resp.ok, resp.text)
            sciname_hits = [
                doc['scientific_name']
                for doc in resp.json()['result'][0]['results']
            ]
            assert_in_method = self.assertIn if st in search_text_exp_hit else self.assertNotIn
            assert_in_method(
                sciname_target,
                sciname_hits,
                f"target: {sciname_target}, query: {st}, sciname_hits: {sciname_hits}"
            )

    def request(self, rpc):
        return requests.post(
            api_url(),
            data=json.dumps(rpc),
            verify=verify_ssl()
        )
