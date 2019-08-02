# Taxonomy API for KBase using the Relation Engine

This is an API for taxonomy data (updated from [taxon_api](https://github.com/kbase/taxon_api)) that queries the relation engine.

## API

JSON RPC requests can be made to to the root path of the URL as a POST request with a json body.

### Responses

The RPC `"result"` field has the following JSON schema, representing query results from RE:

```json
{ "type": "object",
  "properties": {
    "count": {"type": "integer", "title": "Result count"},
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "properties": {
          "_id": {"type": "string", "title": "RE document ID"},
        }
      }
    }
  }
}
```

### get_taxon(params)

Fetch the document data for a single taxon by ID.

Example request:

```sh
curl -d '{"method": "get_taxon", "params": {"id": "ncbi_taxon/100"}}' <url>
```

Example response:

```json
{
}
```

Request params schema:

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "title": "Relation engine document ID"
      "examples": ["ncbi_taxon/100"]
   }
  }
}
```

For the response schema, see the **Responses** section above.

### get_ancestors(params)

### get_descendants(params)

```sh
params='{"method": "get_ancestors", "params": {"taxon_id": 123}}'
curl -d $params http://server/api/v1/rpc
```

Returns a list of taxa

## Development

Run tests with `make test`
