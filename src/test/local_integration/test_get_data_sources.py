from src.test.test_base import TestBase

# Tests for get_data_sources

# These tests may be run against a Tax API which uses a local
# RE with data sources loaded.
# Initial data sources are included in the RE codebase.


class TestGetDataSources(TestBase):

    # Happy path testing

    def test_get_data_sources_all_null_ns(self):
        """Test a call to get sources without filtering"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{'ns': None}]
        })
        self.assertTrue(resp.ok, resp.text)
        jsonrpc_response = resp.json()
        result = self.assert_is_result_response(jsonrpc_response)
        sources = result.get('sources')
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 4)

    def test_get_data_sources_all_missing_ns(self):
        """Test a call to get sources without filtering"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{}]
        })
        self.assertTrue(resp.ok, resp.text)
        jsonrpc_response = resp.json()
        result = self.assert_is_result_response(jsonrpc_response)
        sources = result.get('sources')
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 4)

    def test_get_data_sources_all_no_params(self):
        """Test a call to get sources without filtering"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': []
        })
        self.assertTrue(resp.ok, resp.text)
        jsonrpc_response = resp.json()
        result = self.assert_is_result_response(jsonrpc_response)
        sources = result.get('sources')
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 4)

    def test_get_data_sources_with_filtering_one(self):
        """Test a call to get sources without filtering"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{
                'ns': ['ncbi_taxonomy']
            }]
        })
        self.assertTrue(resp.ok, resp.text)
        jsonrpc_response = resp.json()
        result = self.assert_is_result_response(jsonrpc_response)
        sources = result.get('sources')
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 1)

    def test_get_data_sources_with_filtering_three(self):
        """Test a call to get sources without filtering"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{
                'ns': ['ncbi_taxonomy', 'gtdb', 'rdp_taxonomy']
            }]
        })
        self.assertTrue(resp.ok, resp.text)
        jsonrpc_response = resp.json()
        result = self.assert_is_result_response(jsonrpc_response)
        sources = result.get('sources')
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 3)

    # Error conditions

    def test_get_data_sources_bad_ns(self):
        """Test a call to get sources with an ns parameter of the wrong type"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{
                'params': [{'ns': 1}]
            }]
        })
        self.assertTrue(resp.status_code == 400, 'Expected the response to have status code 400')
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32602, 'Invalid params')

    def test_get_data_sources_provide_undefined_param(self):
        """Test a call to get sources an parameter not defined by the schema"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
            'params': [{
                'params': [{'foo': 'bar'}]
            }]
        })
        self.assertTrue(resp.status_code == 400, 'Expected the response to have status code 400')
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32602, 'Invalid params')

    def test_get_data_sources_missing_method(self):
        """Test a call to get sources with missing method"""
        resp = self.request({
            'version': '1.1',
            'params': [{
                'params': [{'ns': 'ncbi_taxonomy'}]
            }]
        })
        self.assertTrue(resp.status_code == 400, 'Expected the response to have status code 400')
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request')

    def test_get_data_sources_missing_params(self):
        """Test a call to get sources with missing params"""
        resp = self.request({
            'version': '1.1',
            'method': 'taxonomy_re_api.get_data_sources',
        })
        self.assertTrue(resp.status_code == 400, 'Expected the response to have status code 400')
        rpc_response = resp.json()
        self.assert_is_error_response(rpc_response, -32600, 'Invalid request')
