import json
import unittest
import requests
import os

_URL = os.environ.get('API_URL', 'http://localhost:5000')


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

    def test_get_lineage(self):
        """Test a call to get ancestors of a taxon."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_lineage',
                'params': [{'id': '100', 'ns': 'ncbi_taxonomy'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 8)
        ranks = [r['rank'] for r in result['results']]
        expected_ranks = ['no rank', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus']
        self.assertEqual(ranks, expected_ranks)

    def test_get_children(self):
        """Test a call to get direct descendants by ID."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_children',
                'params': [{'id': '28211', 'ns': 'ncbi_taxonomy'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 20)
        self.assertTrue(result['total_count'] > 20)
        ranks = {r['rank'] for r in result['results']}
        expected_ranks = {'order', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_children_search(self):
        """Test a call to get direct descendants by ID and search on them."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_children',
                'params': [{'id': '28211', 'ns': 'ncbi_taxonomy', 'search_text': 'caulobacterales'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 1)

    def test_get_siblings(self):
        """Test a call to get taxon siblings by taxon ID."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_siblings',
                'params': [{'id': '100', 'ns': 'ncbi_taxonomy'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 20)
        self.assertTrue(result['total_count'] > 20)
        ranks = {r['rank'] for r in result['results']}
        self.assertEqual(ranks, {'species'})

    def test_get_taxon(self):
        """Test a call to fetch a taxon by id."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_taxon',
                'params': [{'id': '100', 'ns': 'ncbi_taxonomy'}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['id'], '100')

    def test_search_taxa(self):
        """Test a call to search taxa by scientific name."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.search_taxa',
                'params': [{'ns': 'ncbi_taxonomy', 'search_text': 'prefix:rhodobact', 'limit': 10, 'offset': 20}]
            })
        )
        self.assertTrue(resp.ok)
        body = resp.json()
        result = body['result'][0]
        self.assertTrue(result['total_count'] > 10)
        self.assertEqual(len(result['results']), 10)
        for result in result['results']:
            self.assertTrue('rhodobact' in result['scientific_name'].lower())

    def test_get_associated_ws_objects(self):
        """Test a call to get associated workspace objects from a taxon id."""
        resp = requests.post(
            _URL,
            data=json.dumps({
                'method': 'taxonomy_re_api.get_associated_ws_objects',
                'params': [{'taxon_id': '562', 'taxon_ns': 'ncbi_taxonomy'}]
            })
        )
        print('associated objects response', resp.text)
        self.assertTrue(resp.ok)
