import json
import unittest
import requests

_URL = 'http://localhost:5000'


class TestIntegration(unittest.TestCase):

    def test_status(self):
        """Test the health check request."""
        resp = requests.get(_URL)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.json()['status'], 'ok')

    def test_get_ancestors(self):
        """Test a call to fetch a taxon by id."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_ancestors',
                'params': {'taxonomy_id': '100'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(len(body['result']['results']), 9)
