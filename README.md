# Taxonomy API for KBase using the Relation Engine

This is an API for taxonomy data (updated from [taxon_api](https://github.com/kbase/taxon_api)) that queries the relation engine.

This service is a registered as a KBase dynamic service under the module name `taxonomy_re_api` and is managed by the Catalog.

## API

JSON RPC requests can be made to to the root path of the URL as a POST request with a json body.

The API follows two conventions followed by KBase APIs:

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

### taxonomy_re_api.get_taxon_from_ws_obj(params)

Fetch the taxon document from a versioned workspace reference.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_taxon_from_ws_obj.yaml)

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_associated_ws_objects(params)

Fetch all workspace objects associated with a given taxon.

This endpoint is authorization over workspace objects by passing a KBase token via the `Authorization` header.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_associated_ws_objects.yaml)

See the section below about the `select` parameter for further details on it.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_lineage(params)

Fetch the ancestors for a taxon vertex.

[Request parameters schema (wrapped in an array)](src/server/schemas/get_lineage.yaml)

See the section below about the `select` parameter for further details on it.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_children(params)

Fetch the direct descendants for a taxon vertex.

The optional "search_text" parameter can be specified to search on scientific name for the children. See the **Search text** section below for details on the `search_text` parameter.

[Request parameters schema (wrapped in an array)](/src/server/schemas/get_children.yaml)

See the section below about the `select` parameter for further details on it.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_siblings(params)

Fetch the siblings for a taxon.

[Request parameters schema (wrapped in an array)](/src/server/schemas/get_siblings.yaml)

See the section below about the `select` parameter for further details on it.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.search_species(params)

Search for species or strains based on a scientific name. Similar to `search_taxa`, but is a stripped down, faster query.

Paginate with the "limit" and "offset" parameters.

[Request parameters schema (wrapped in an array)](src/server/schemas/search_species.yaml)

See the section below about the `select` parameter for further details on it.

See the **Search text** section below for details on the syntax you can use in the search text.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.search_taxa(params)

Search for taxa based on scientific name.

Paginate with the "limit" and "offset" parameters.

[Request parameters schema (wrapped in an array)](src/server/schemas/search_taxa.yaml)

See the section below about the `select` parameter for further details on it.

See the **Search text** section below for details on the syntax you can use in the search text.

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_data_sources(params)

Returns all or matching set of taxonomy data source descriptions.

The only parameter is the optional `ns`, which may be used to filter the returned data sources by namespace. There is a 1-1 correspondence between namespaces (e.g. `ncbi_taxonomy`) and a data source descriptions.

#### Params

[Request parameters schema (wrapped in an array)](src/server/schemas/get_data_sources.yaml)
#### Result

Usage:

* omit the params or supply an empty object to return all taxonomy data sources
* supply a list of 1 or more namespaces in the `ns` parameter to return just those data sources

An implication of this design is that supplying an `ns` with an empty list will return no data sources.

#### Example

##### Return all data sources

This RPC request returns all data_sources by omitting the parameter. (Remember, KBase service params are the (almost) always the first element of the JSON-RPC params field, which must be an array.)

```json
{
	"version": "1.1",
	"method": "taxonomy_re_api.get_data_sources",
	"params": []
}
```

or by supplying the params, but omitting the `ns` param:

```json
{
	"version": "1.1",
	"method": "taxonomy_re_api.get_data_sources",
	"params": [{}]
}
```

##### Return NCBI data source

```json
{
	"version": "1.1",
	"method": "taxonomy_re_api.get_data_sources",
	"params": [{"ns": ["ncbi_taxonomy"]}]
}
```

##### Return NCBI and GTDB data source

```json
{
	"version": "1.1",
	"method": "taxonomy_re_api.get_data_sources",
	"params": [{"ns": ["ncbi_taxonomy", "gtdb"]}]
}
```

## Search text

Within a `"search_text"` field, you can use this Arangodb fulltext search syntax to refine the results:

* Separate search terms by comma: "rhodobacter,pseudomonas"
* To search against a term **OR** another term, use a "|" prefix: "rhodobacter,|pseudomonas"
* To search by prefix, use the "prefix:" prefix: "prefix:rhodo,|prefix:pseudo"
* To exclude a term, use `"-term"`

See the ADB documentation for further details: https://www.arangodb.com/docs/stable/aql/functions-fulltext.html

## The `select` parameter

All of the methods (except `get_taxon` and `get_data_sources`) can accept a `select` parameter, which
allows you to control which fields you would like returned. Set it to an array
of the field names that you want. This is useful if you would like to reduce
the size of the response body. If you don't set this parameter, all fields
will be returned in the results.

## Development

### Unit tests

Run unit tests with `make test`

### Integration tests

You can also test the API against a live url. For example:

```
export API_URL="https://ci.kbase.us/dynserv/ecc3fcf41201e66ba6e2d8101195ea29bffba050.taxonomy-re-api"
python -m unittest src/test/integration/test_integration.py

python -m unittest discover -s src/test/integration 
```
