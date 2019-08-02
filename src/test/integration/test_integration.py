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
        """Test a call to get ancestors of a taxon."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_ancestors',
                'params': {'id': 'ncbi_taxon/100'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(len(body['result']['results']), 9)
        ranks = [r['rank'] for r in body['result']['results']]
        expected_ranks = ['genus', 'family', 'order', 'class', 'phylum', 'superkingdom', 'no rank', 'no rank', 'no rank']  # noqa
        self.assertEqual(ranks, expected_ranks)

    def test_get_descendants(self):
        """Test a call to get descendants by ID."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_descendants',
                'params': {'id': 'ncbi_taxon/28211'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(body['result']['count'], 21)
        ranks = {r['rank'] for r in body['result']['results']}
        expected_ranks = {'order', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_descendants_2levels(self):
        """Test a call to get 2 levels of descendants for a taxon."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_descendants',
                'params': {'id': 'ncbi_taxon/28211', 'levels': 2}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(body['result']['count'], 717)
        ranks = {r['rank'] for r in body['result']['results']}
        expected_ranks = {'order', 'family', 'species', 'genus', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_siblings(self):
        """Test a call to get taxon siblings by taxon ID."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_siblings',
                'params': {'id': 'ncbi_taxon/100'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(body['result']['count'], 69)
        ranks = {r['rank'] for r in body['result']['results']}
        self.assertEqual(ranks, {'species', 'no rank'})

    def test_get_taxon(self):
        """Test a call to fetch a taxon by id."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'get_taxon',
                'params': {'id': 'ncbi_taxon/100'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(body['result']['count'], 1)
        self.assertEqual(body['result']['results'][0]['_id'], 'ncbi_taxon/100')

    def test_search_taxa(self):
        """Test a call to search taxa by scientific name."""
        resp = requests.post(
            _URL + '/rpc',
            data=json.dumps({
                'method': 'search_taxa',
                'params': {'search_text': 'prefix:rhodobact'}
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        self.assertEqual(body['result']['count'], 20)
        for result in body['result']['results']:
            self.assertTrue(result['scientific_name'].lower().startswith('rhodobact'))
