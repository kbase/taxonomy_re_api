import json
import unittest
import requests

_URL = 'http://localhost:5000'


class TestIntegration(unittest.TestCase):

    # TODO invalid http method
    # TODO invalid json body
    # TODO missing method
    # TODO empty method
    # TODO unknown method
    # TODO missing params
    # TODO empty params (empty list and list of empty obj)
    # TODO invalid id
    # TODO valid id but nonexistent
    # TODO error response from RE API

    def test_status(self):
        """Test the health check request."""
        resp = requests.get(_URL)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.json()['result'][0]['status'], 'ok')

    def test_get_ancestors(self):
        """Test a call to get ancestors of a taxon."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_ancestors',
                'params': [{'id': 'ncbi_taxon/100'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 9)
        ranks = [r['rank'] for r in result['results']]
        expected_ranks = ['genus', 'family', 'order', 'class', 'phylum', 'superkingdom', 'no rank', 'no rank', 'no rank']  # noqa
        self.assertEqual(ranks, expected_ranks)

    def test_get_descendants(self):
        """Test a call to get descendants by ID."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_descendants',
                'params': [{'id': 'ncbi_taxon/28211'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(result['count'], 21)
        ranks = {r['rank'] for r in result['results']}
        expected_ranks = {'order', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_descendants_2levels(self):
        """Test a call to get 2 levels of descendants for a taxon."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_descendants',
                'params': [{'id': 'ncbi_taxon/28211', 'levels': 2}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(result['count'], 717)
        ranks = {r['rank'] for r in result['results']}
        expected_ranks = {'order', 'family', 'species', 'genus', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_siblings(self):
        """Test a call to get taxon siblings by taxon ID."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_siblings',
                'params': [{'id': 'ncbi_taxon/100'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(result['count'], 69)
        ranks = {r['rank'] for r in result['results']}
        self.assertEqual(ranks, {'species', 'no rank'})

    def test_get_taxon(self):
        """Test a call to fetch a taxon by id."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_taxon',
                'params': [{'id': 'ncbi_taxon/100'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['results'][0]['_id'], 'ncbi_taxon/100')

    def test_search_taxa(self):
        """Test a call to search taxa by scientific name."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.search_taxa',
                'params': [{'search_text': 'prefix:rhodobact', 'page': 2, 'page_len': 10}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(result['count'], 10)
        for result in result['results']:
            self.assertTrue(result['scientific_name'].lower().startswith('rhodobact'))
