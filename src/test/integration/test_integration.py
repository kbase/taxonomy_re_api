import unittest
import requests

_URL = 'http://localhost:5000'


class TestIntegration(unittest.TestCase):

    def test_status(self):
        """Test the health check request."""
        resp = requests.get(_URL)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.json()['status'], 'ok')

    def test_fetch_taxon(self):
        """Test a call to fetch a taxon by id."""
        resp = requests.get(_URL + '/taxa/1')
        self.assertTrue(resp.ok)
        print('resp', resp.json())
