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
        self.assertEqual(ranks, {'species', 'no rank'})
        for result in result['results']:
            self.assertTrue('rhodobact' in result['scientific_name'].lower())

    def test_search_species__syntax(self):
        """
        Test a call to search species/strains when search text has non-alphanumerics
        """
        sciname_target = 'Bacillus sp. (in: Bacteria)'
        search_text_expect_hit = [
            'Bacillus sp. (in: Bacteria)',
            'bacillus sp. (in: bacteria)',
            'bacillus sp in bacteria',
            # 'bac sp in:bac',  AQL won't tokenize in:bac
            # 'bac sp',  target won't be in top 20
            'prefix:Bacillus sp. (in: Bacteria)',
            # 'prefix:bac sp',
            # 'bacillus sp',  target won't be in top 20
            'in in bacteria BACILLUS'
        ]
        search_text_expect_miss = [
            'bacillus ss',
            'bacillusspinbacteria',
        ]
        self.assert_query_results(sciname_target, search_text_expect_hit, search_text_expect_miss)

        sciname_target = 'Bacillus sp. 1011TES4D14,1'
        search_text_expect_hit = [
            'Bacillus sp. 1011TES4D14,1',
            'Bacillus sp. 1011',
            'Bacillus 1011 1',
            'bacillus 1011tes4d14,1',
            '1011tes4d14',
            'bac sp 1011',
            'bac sp 1011 bac sp sp'
        ]
        search_text_expect_miss = [
            'bacillus ss',
            'bacsp1011',
        ]
        self.assert_query_results(sciname_target, search_text_expect_hit, search_text_expect_miss)

        sciname_target = 'Candidatus Woesearchaeota archaeon CG1_02_57_44'
        search_text_expect_hit = [
            '  Candidatus  Woesearchaeota  CG1_ ',
            'archaeon candidatus woesearchaeota',
            'archaeon candidatus CG1 woesearchaeota',
        ]
        search_text_expect_miss = [
            '_02_57',
        ]
        self.assert_query_results(sciname_target, search_text_expect_hit, search_text_expect_miss)

        sciname_target = 'Nanoarchaeota archaeon SCGC AAA011-D5'
        search_text_expect_hit = [
            'AAA011 D5',
            'AAA011-D5',
            'Nanoarchaeota archaeon SCGC AAA011-D5;',
            'nanoarchaeota aaa011'
        ]
        search_text_expect_miss = [
            'AAA011D5',
        ]
        self.assert_query_results(sciname_target, search_text_expect_hit, search_text_expect_miss)

    def test_search_species__exact_hit(self):
        """
        Test a call to search species/strains when search text has non-alphanumerics
        """
        queries = [
            # --- single character, or not
            "uncultured bacterium 'eubacterium sp.'",
            '[Bacillus] caldolyticus',
            "Microcystis sp. 'BC 84/1'",  # 1
            'Influenza C virus (C/PIG/Beijing/439/1982)',  # c
            'Bovine herpesvirus type 1.1 (strain P8-2)',  # 1 2
            'Porcine transmissible gastroenteritis coronavirus strain FS772/70',
            'Tuber borchii symbiont b-Z43',
            'Salmonella enterica subsp. houtenae serovar 16:z4,z32:--',
            'mycorrhizal fungus XII-1 of Orchis morio',  # 1
            'Influenza B virus (B/Xuanwu/23/82)',  # b
            'Influenza A virus PX8-XIII(A/USSR/90/77(H1N1)xA/Pintail Duck/Primorie/695/76(H2N3))',  # a
            'Xanthomonas-like sp. V4.BO.41',
            'Influenza B virus (B/Ann Arbor/1/1966 [cold-adapted and wild- type])',  # b 1
            "Rhopalocarpus sp. 'M.F.F. 11-13-97'",  # m f
            # --- special tokenization
            "Rhopalocarpus sp. 'M.F.F. 11-13-97'",
            'Lactococcus phage 936 group phage Phi13.16',
            'Hiatomyia sp. BOLD:AAZ5940',
            'Saprochaete clavata CNRMA 12.647',
            'Klebsormidium sp. BIOTA 14621.10.47',
            'Potamosiphon austaliensis FHC0914.01',
            'Pseudogobio cf. esocinus CBM:ZF:12684',
            'Klebsormidium sp. BIOTA 14615.5a',
            'Bovine herpesvirus type 1.2 strain Q3932',
            'Bovine herpesvirus type 1.1 (strain Cooper)',
            'Bovine herpesvirus type 1.1 (strain P8-2)',
            # --- not in top 20, in this case bc prefix of lots others
            'Norovirus GII.9',
            'Corticiaceae sp.',
            # --- dups, in the last TS, but < 20
            'environmental samples',
            'Boloria chariclea',
            'environmental samples',
            'Listeria sp. FSL_L7-1582',
        ]
        expired = [
            'Hiatomyia sp. BOLD:AAZ5940',
            'Saprochaete clavata CNRMA 12.647',
            'Klebsormidium sp. BIOTA 14621.10.47',
            'Pseudogobio cf. esocinus CBM:ZF:12684',
            'Klebsormidium sp. BIOTA 14615.5a',
            'Norovirus GII.9',
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assert_query_results(
                    query,
                    [query],
                    expired=query in expired
                )

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
