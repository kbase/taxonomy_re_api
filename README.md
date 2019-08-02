# Taxonomy API for KBase using the Relation Engine

This is an API for taxonomy data (updated from [taxon_api](https://github.com/kbase/taxon_api)) that queries the relation engine.

This service is a registered as a KBase dynamic service under the module name `taxonomy_re_api`.

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
        "description": "Standard RE database fields, plus all additional document-specific fields.",
        "properties": {
          "_id": {"type": "string", "title": "RE document ID", "examples": ["ncbi_taxon/100"]},
          "_key": {"type": "string", "title": "RE document key", "examples": ["100"]},
          "_rev": {"type": "string", "title": "DB revision ID"}
        }
      }
    },
    "stats": {
      "type": "object",
      "description": "RE query execution meta-info"
    }
  }
}
```

"_id" is unique across the database, while "_key" is only unique within its collection.

### get_taxon(params)

Fetch the document data for a single taxon by ID.

Example request:

```sh
curl -d '{"method": "get_taxon", "params": {"id": "ncbi_taxon/100"}}' <url>
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "jsonrpc": "2.0",
    "id": "7d802521-10a7-48b2-ab99-105390ef72fa",
    "result": {
        "count": 1,
        "cursor_id": null,
        "has_more": false,
        "results": [
            {
                "NCBI_taxon_id": 100,
                "_id": "ncbi_taxon/100",
                "_key": "100",
                "_rev": "_Y8a52eC-_D",
                "aliases": [
                    {
                        "canonical": ["ancylobacter", "aquaticus", "orskov", "raj"],
                        "category": "authority",
                        "name": "Ancylobacter aquaticus (Orskov 1928) Raj 1983"
                    }
                ],
                "canonical_scientific_name": ["ancylobacter", "aquaticus"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Ancylobacter aquaticus"
            }
        ],
        "stats": {
            "executionTime": 0.001932621,
            "filtered": 0,
            "httpRequests": 0,
            "scannedFull": 0,
            "scannedIndex": 1,
            "writesExecuted": 0,
            "writesIgnored": 0
        }
    }
}
```

</div>
</details>

Request parameters schema:

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
   }
  }
}
```

For the response schema, see the **Responses** section above.

### get_ancestors(params)

Fetch the ancestors for a taxon vertex.

Example request:

```sh
curl -d '{"method": "get_ancestors", "params": {"id": "ncbi_taxon/100"}}' <url>
```

Example response:

<details>
<summary>Example response:</summary>
<div>

```json
{
    "jsonrpc": "2.0",
    "id": "d6fa9908-849a-4421-931a-f01328a769a9",
    "result": {
        "count": 9,
        "cursor_id": null,
        "has_more": false,
        "results": [
            {
                "NCBI_taxon_id": 99,
                "_id": "ncbi_taxon/99",
                "_key": "99",
                "_rev": "_Y8a52ga--h",
                "aliases": [],
                "canonical_scientific_name": ["ancylobacter"],
                "gencode": "11",
                "rank": "genus",
                "scientific_name": "Ancylobacter"
            },
            {
                "NCBI_taxon_id": 335928,
                "_id": "ncbi_taxon/335928",
                "_key": "335928",
                "_rev": "_Y8bDLTy-_X",
                "aliases": [],
                "canonical_scientific_name": ["xanthobacteraceae"],
                "gencode": "11",
                "rank": "family",
                "scientific_name": "Xanthobacteraceae"
            },
            {
                "NCBI_taxon_id": 356,
                "_id": "ncbi_taxon/356",
                "_key": "356",
                "_rev": "_Y8a52g6--J",
                "aliases": [],
                "canonical_scientific_name": ["rhizobiales"],
                "gencode": "11",
                "rank": "order",
                "scientific_name": "Rhizobiales"
            },
            {
                "NCBI_taxon_id": 28211,
                "_id": "ncbi_taxon/28211",
                "_key": "28211",
                "_rev": "_Y8a6Mdm--J",
                "aliases": [],
                "canonical_scientific_name": ["alphaproteobacteria"],
                "gencode": "11",
                "rank": "class",
                "scientific_name": "Alphaproteobacteria"
            },
            {
                "NCBI_taxon_id": 1224,
                "_id": "ncbi_taxon/1224",
                "_key": "1224",
                "_rev": "_Y8a52g---p",
                "aliases": [],
                "canonical_scientific_name": ["proteobacteria"],
                "gencode": "11",
                "rank": "phylum",
                "scientific_name": "Proteobacteria"
            },
            {
                "NCBI_taxon_id": 2,
                "_id": "ncbi_taxon/2",
                "_key": "2",
                "_rev": "_Y8a52f6--L",
                "aliases": [],
                "canonical_scientific_name": ["bacteria"],
                "gencode": "11",
                "rank": "superkingdom",
                "scientific_name": "Bacteria"
            },
            {
                "NCBI_taxon_id": 131567,
                "_id": "ncbi_taxon/131567",
                "_key": "131567",
                "_rev": "_Y8a9OHm--l",
                "aliases": [],
                "canonical_scientific_name": ["cellular", "organisms"],
                "gencode": "1",
                "rank": "no rank",
                "scientific_name": "cellular organisms"
            },
            {
                "NCBI_taxon_id": 1,
                "_id": "ncbi_taxon/1",
                "_key": "1",
                "_rev": "_Y8a52em-_b",
                "aliases": [],
                "canonical_scientific_name": ["root"],
                "gencode": "1",
                "rank": "no rank",
                "scientific_name": "root"
            },
            {
                "NCBI_taxon_id": 1,
                "_id": "ncbi_taxon/1",
                "_key": "1",
                "_rev": "_Y8a52em-_b",
                "aliases": [],
                "canonical_scientific_name": ["root"],
                "gencode": "1",
                "rank": "no rank",
                "scientific_name": "root"
            }
        ],
        "stats": {
            "executionTime": 0.1159160137,
            "filtered": 0,
            "httpRequests": 61,
            "scannedFull": 0,
            "scannedIndex": 9,
            "writesExecuted": 0,
            "writesIgnored": 0
        }
    }
}
```

</div>
</details>

Request parameters schema:

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
   }
  }
}
```

For the response schema, see the **Responses** section above.

### get_descendants(params)

Fetch the descendants for a taxon vertex. Defaults to direct children, but can be specified to return multiple levels of children.

Example request:

```sh
curl -d '{"method": "get_descendants", "params": {"id": "ncbi_taxon/28211"}}' <url>
```

Example response:

<details>
<summary>Example response:</summary>
<div>

```json
{
    "jsonrpc": "2.0",
    "id": "da3803b6-0ca9-412d-adbd-15fa329649a4",
    "result": {
        "count": 21,
        "cursor_id": null,
        "has_more": false,
        "results": [
            {
                "NCBI_taxon_id": 1191478,
                "_id": "ncbi_taxon/1191478",
                "_key": "1191478",
                "_rev": "_Y8bYbFC--a",
                "aliases": [],
                "canonical_scientific_name": ["magnetococcales"],
                "gencode": "11",
                "rank": "order",
                "scientific_name": "Magnetococcales"
            },
            {
                "NCBI_taxon_id": 343329,
                "_id": "ncbi_taxon/343329",
                "_key": "343329",
                "_rev": "_Y8bDLSm--P",
                "aliases": [],
                "canonical_scientific_name": ["kopriimonadales"],
                "gencode": "11",
                "rank": "order",
                "scientific_name": "Kopriimonadales"
            },
            {
                "NCBI_taxon_id": 597358,
                "_id": "ncbi_taxon/597358",
                "_key": "597358",
                "_rev": "_Y8bKela--5",
                "aliases": [],
                "canonical_scientific_name": ["kiloniellales"],
                "gencode": "11",
                "rank": "order",
                "scientific_name": "Kiloniellales"
            }
        ]
    }
}
```

</div>
</details>

Request parameters schema:

```json
{ "type": "object",
  "required": ["id"],
  "optional": ["levels"],
  "properties": {
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    },
    "levels": {
      "type": "integer",
      "default": 1,
      "description": "Number of descendant levels to traverse and return."
    }
  }
}
```

For the response schema, see the **Responses** section above.

### get_siblings(params)

Fetch the siblings for a taxon.

Example request:

```sh
curl -d '{"method": "get_siblings", "params": {"id": "ncbi_taxon/100"}}' <url>
```

Example response:

<details>
<summary>Example response:</summary>
<div>

```json
{
    "jsonrpc": "2.0",
    "id": "ec9e970b-0e4b-4c79-ae5d-4d37e45772a1",
    "result": {
        "count": 69,
        "cursor_id": null,
        "has_more": false,
        "results": [
            {
                "NCBI_taxon_id": 459519,
                "_id": "ncbi_taxon/459519",
                "_key": "459519",
                "_rev": "_Y8bG08O--Q",
                "aliases": [],
                "canonical_scientific_name": ["ancylobacter", "oerskovii"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Ancylobacter oerskovii"
            },
            {
                "NCBI_taxon_id": 1267549,
                "_id": "ncbi_taxon/1267549",
                "_key": "1267549",
                "_rev": "_Y8batdG--2",
                "aliases": [],
                "canonical_scientific_name": ["ancylobacter", "sp", "tet"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Ancylobacter sp. Tet-1"
            },
            {
                "NCBI_taxon_id": 1270368,
                "_id": "ncbi_taxon/1270368",
                "_key": "1270368",
                "_rev": "_Y8batbW--p",
                "aliases": [],
                "canonical_scientific_name": ["ancylobacter", "sp", "isom", "otu"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Ancylobacter sp. ISOM336_OTU3086"
            }
        ],
        "stats": {
            "executionTime": 0.2142424583,
            "filtered": 1,
            "httpRequests": 61,
            "scannedFull": 0,
            "scannedIndex": 72,
            "writesExecuted": 0,
            "writesIgnored": 0
        }
    }
}
```

</div>
</details>

Request parameters schema:

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    }
  }
}
```

For the response schema, see the **Responses** section above.

### search_taxa(params)

Search for taxa based on scientific name.

Within `"search_text"`, you can use this syntax to refine the results:
* Separate search terms by comma: "rhodobacter,pseudomonas"
* To search against a term **OR** another term, use a "|" prefix: "rhodobacter,|pseudomonas"
* To search by prefix, use the "prefix:" prefix: "prefix:rhodo,|prefix:pseudo"

Results are paginated to 20 per page by default. You can pass a `"page"` parameter to get an offset of the results. This parameter defaults to `1`, meaning fetch the first 20 results. Setting "page" to 5 would give you results 101 through 120.

Pass a `"page_len"` param to customize the page length.

Example request:

```sh
curl -d '{"method": "search_taxa", "params": {"search_text": "prefix:rhodo,|prefix:psuedo"}}' <url>
```

Example response:

<details>
<summary>Example response:</summary>
<div>

```json
{
    "jsonrpc": "2.0",
    "id": "092ad091-7218-4c28-92f4-2aa91a204a13",
    "result": {
        "count": 4,
        "cursor_id": null,
        "has_more": false,
        "results": [
            {
                "NCBI_taxon_id": 1087,
                "_id": "ncbi_taxon/1087",
                "_key": "1087",
                "_rev": "_Y8a52e6--n",
                "aliases": [],
                "canonical_scientific_name": ["rhodovibrio", "salinarum"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Rhodovibrio salinarum"
            },
            {
                "NCBI_taxon_id": 1088,
                "_id": "ncbi_taxon/1088",
                "_key": "1088",
                "_rev": "_Y8a52e6--p",
                "aliases": [],
                "canonical_scientific_name": ["rhodovibrio", "sodomensis"],
                "gencode": "11",
                "rank": "species",
                "scientific_name": "Rhodovibrio sodomensis"
            },
            {
                "NCBI_taxon_id": 29898,
                "_id": "ncbi_taxon/29898",
                "_key": "29898",
                "_rev": "_Y8a6MZO--X",
                "aliases": [],
                "canonical_scientific_name": ["rhodotorula", "graminis"],
                "gencode": "1",
                "rank": "species",
                "scientific_name": "Rhodotorula graminis"
            },
            {
                "NCBI_taxon_id": 31491,
                "_id": "ncbi_taxon/31491",
                "_key": "31491",
                "_rev": "_Y8a6MZS--f",
                "aliases": [][]
                "canonical_scientific_name": ["rhodogorgonales"],
                "gencode": "1",
                "rank": "order",
                "scientific_name": "Rhodogorgonales"
            }
        ],
        "stats": {
            "executionTime": 0.0577430725,
            "filtered": 0,
            "httpRequests": 31,
            "scannedFull": 0,
            "scannedIndex": 20,
            "writesExecuted": 0,
            "writesIgnored": 0
        }
    }
}
```

</div>
</details>

Request parameters schema:

```json
{ "type": "object",
  "required": ["search_text"],
  "properties": {
    "search_text": {
      "type": "string",
      "title": "Scientific name search query text.",
      "examples": ["prefix:rhodo,|psueodmonas"]
    },
    "page": {
      "type": "integer",
      "default": 1,
      "description": "Page number of results to return"
    },
    "page_len": {
      "type": "integer",
      "default": 20,
      "maximum": 1000,
      "description": "Length of results to return."
    }
  }
}
```

For the response schema, see the **Responses** section above.

## Development

Run tests with `make test`
