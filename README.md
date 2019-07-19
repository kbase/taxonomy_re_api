# Taxonomy API for KBase using the Relation Engine

This is an API for taxonomy data (updated from [taxon_api](https://github.com/kbase/taxon_api)) that queries the relation engine.

## API

OpenAPI docs: [TODO](todo)

### get_ancestors(taxon_id) -> [taxa]

```sh
params='{"method": "get_ancestors", "params": {"taxon_id": 123}}'
curl -d $params http://server/api/v1/rpc
```

Returns a list of taxa

## Development

Run tests with `make test`
