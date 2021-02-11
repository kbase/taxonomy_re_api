import requests
from src.test.test_base import TestBase, api_url, verify_ssl

# These tests must be run against an instance of Tax API which uses CI RE,
# unless you have a local RE with the NCBI taxonomy loaded.


class TestIntegration(TestBase):

    def test_status(self):
        """Test the health check request."""
        resp = requests.get(api_url(), verify=verify_ssl())
        self.assertTrue(resp.ok, resp.text)
        self.assertEqual(resp.json()['result'][0]['status'], 'ok')

    def test_get_lineage(self):
        """Test a call to get ancestors of a taxon."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_lineage',
            'params': [{'id': '100', 'ns': 'ncbi_taxonomy', 'select': ['rank', 'id']}]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 8)
        ranks = [r['rank'] for r in result['results']]
        expected_ranks = ['no rank', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus']
        self.assertEqual(ranks, expected_ranks)

    def test_get_children(self):
        """Test a call to get direct descendants by ID."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_children',
            'params': [{'id': '28211', 'ns': 'ncbi_taxonomy'}]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 20)
        self.assertTrue(result['total_count'] > 20)
        ranks = {r['rank'] for r in result['results']}
        expected_ranks = {'order', 'no rank'}
        self.assertEqual(ranks, expected_ranks)

    def test_get_children_search(self):
        """Test a call to get direct descendants by ID and search on them."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_children',
            'params': [{'id': '28211', 'ns': 'ncbi_taxonomy', 'search_text': 'caulobacterales', 'select': ['id']}]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0], {'id': '204458', 'ns': 'ncbi_taxonomy'})

    def test_get_siblings(self):
        """Test a call to get taxon siblings by taxon ID."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_siblings',
            'params': [{'id': '287', 'ns': 'ncbi_taxonomy', 'select': ['rank', 'scientific_name']}],
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertTrue(len(result['results']) > 1)
        self.assertTrue(result['total_count'] > 1)
        ranks = {r['rank'] for r in result['results']}
        self.assertEqual(ranks, {'species', 'species subgroup'})

    def test_get_taxon(self):
        """Test a call to fetch a taxon by id."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon',
            'params': [{'id': '100', 'ns': 'ncbi_taxonomy'}]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['id'], '100')

    def test_search_taxa(self):
        """Test a call to search taxa by scientific name."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.search_taxa',
            'params': [{
                'ns': 'ncbi_taxonomy',
                'search_text': 'prefix:rhodobact',
                'limit': 10,
                'ranks': ['species'],
                'include_strains': True,
                'offset': 20
            }]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        ranks = set(r['rank'] for r in result['results'])
        self.assertTrue(result['total_count'] > 10)
        self.assertEqual(len(result['results']), 10)
        self.assertEqual(ranks, {'species'})
        for result in result['results']:
            self.assertTrue('rhodobact' in result['scientific_name'].lower())

    def test_search_species_gtdb(self):
        """Test a call to search species/strains."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.search_species',
            'params': [{
                'ns': 'gtdb',
                'search_text': 'prefix:rhodobact',
                'limit': 10,
                'offset': 20
            }]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        ranks = set(r['rank'] for r in result['results'])
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(ranks, {'species'})
        for result in result['results']:
            self.assertTrue('rhodobact' in result['scientific_name'].lower())

    def test_search_species(self):
        """Test a call to search species/strains."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.search_species',
            'params': [{
                'ns': 'ncbi_taxonomy',
                'search_text': 'prefix:rhodobact',
                'limit': 10,
                'offset': 20
            }]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        ranks = set(r['rank'] for r in result['results'])
        self.assertEqual(len(result['results']), 10)
        self.assertEqual(ranks, {'species'})
        for result in result['results']:
            self.assertTrue('rhodobact' in result['scientific_name'].lower())

    def test_get_associated_ws_objects(self):
        """Test a call to get associated workspace objects from a taxon id."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_associated_ws_objects',
            'params': [{'id': '287', 'ns': 'ncbi_taxonomy', 'ts': 1569888060000}]
        })
        self.assertTrue(resp.ok, resp.text)
        body = resp.json()['result'][0]
        self.assertTrue(body['total_count'] > 0)
        ws_infos = [res['ws_obj']['workspace'] for res in body['results']]
        # Assert that we have workspace info in the results
        for ws_info in ws_infos:
            self.assertTrue('narr_name' in ws_info)
            self.assertEqual(ws_info['refdata_source'], 'NCBI RefSeq')

    def test_get_taxon_from_ws_obj(self):
        """Test a call to get a taxon doc from a workspace object id."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_taxon_from_ws_obj',
            'params': [{'obj_ref': '15792:10546:2', 'ns': 'ncbi_taxonomy', 'ts': 1569888060000}]
        })
        self.assertTrue(resp.ok, resp.text)
        result = resp.json()['result'][0]
        self.assertDictContainsSubset({
            'gencode': 11,
            'id': '287',
            'ncbi_taxon_id': 287,
            'rank': 'species',
            'ns': 'ncbi_taxonomy'
        }, result['results'][0])

    def test_search_taxa_rdp(self):
        """Test a call to search taxa on RDP taxonomy."""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.search_taxa',
            'params': [{
                'ns': 'rdp_taxonomy',
                'search_text': 'rhodobacter',
            }]
        })

        self.assertTrue(resp.ok, resp.text)
        body = resp.json()
        result = body['result'][0]
        self.assertEqual(len(result['results']), 20)
        for result in result['results']:
            self.assertTrue('rhodobacter' in result['name'].lower())
