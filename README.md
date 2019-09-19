# Taxonomy API for KBase using the Relation Engine

This is an API for taxonomy data (updated from [taxon_api](https://github.com/kbase/taxon_api)) that queries the relation engine.

This service is a registered as a KBase dynamic service under the module name `taxonomy_re_api`.

## API

JSON RPC requests can be made to to the root path of the URL as a POST request with a json body.

The API follows two unusual conventions followed by other KBase APIs:
* All method names are prefixed by the module name (`taxonomy_re_api.get_taxon` instead of just `get_taxon`)
* All params and results are wrapped in an extra array

### Responses

The RPC `"result"` field has the following JSON schema, representing query results from RE:

The result is always wrapped in an array of one element, following KBase convention.

```yaml
type: array
minItems: 1
maxItems: 1
items:
  type: object
  properties:
    total_count:
      type: integer
      title: Result count (before pagination)
    ts:
      type: integer
      title: Timestamp used in the request
    stats:
      type: object
      description: RE query execution meta-info
    results:
      type: array
      items:
        type: object
        additionalProperties: true
        description: Standard RE database fields, plus all additional document-specific fields.
        properties:
          id:
            type: string
            title: RE document ID
            examples: ["562", "287"]
          ns:
            type: string
            title: Taxonomy namespace
            enum: [ncbi_taxonomy]
          created:
            type: integer
            title: Unix epoch creation time
          expired:
            type: integer
            title: Unix epoch expiration time
```

### Timestamp parameter

Every method for this API can take a `ts` parameter, representing the Unix
epoch time (in milliseconds) of when the document was active in the
database. This is optional and defaults to the current time.

## Methods

### taxonomy_re_api.get_taxon(params)

Fetch the document data for a single taxon by ID.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_taxon.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_associated_ws_objects(params)

Fetch all workspace objects associated with a given taxon.

This endpoint is authorization over workspace objects by passing a KBase token via the `Authorization` header.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_associated_ws_objects.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_lineage(params)

Fetch the ancestors for a taxon vertex.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_lineage.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_children(params)

Fetch the direct descendants for a taxon vertex.

The optional "search_text" parameter can be specified to search on scientific name for the children. See the **Search text** section below for details on the `search_text` parameter.

[Request parameters schema (wrapped in an array)](/src/server/schemas/get_children.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_siblings(params)

Fetch the siblings for a taxon.

[Request parameters schema (wrapped in an array)](/src/server/schemas/get_siblings.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.search_taxa(params)

Search for taxa based on scientific name.

Paginate with the "limit" and "offset" parameters.

[Request parameters schema (wrapped in an array)](src/server/schemas/search_taxa.yaml)

See the **Search text** section below for details on the syntax you can use in the search text.

For the response schema, see the **Responses** section above.

## Search text

Within a `"search_text"` field, you can use this Arangodb fulltext search syntax to refine the results:

* Separate search terms by comma: "rhodobacter,pseudomonas"
* To search against a term **OR** another term, use a "|" prefix: "rhodobacter,|pseudomonas"
* To search by prefix, use the "prefix:" prefix: "prefix:rhodo,|prefix:pseudo"
* To exclude a term, use `"-term"`

See the ADB documentation for further details: https://www.arangodb.com/docs/stable/aql/functions-fulltext.html

## Development

Run tests with `make test`

You can also test the API against a live url. For example:

```
export API_URL="https://ci.kbase.us/dynserv/ecc3fcf41201e66ba6e2d8101195ea29bffba050.taxonomy-re-api"
python -m unittest src/test/integration/test_integration.py
```
