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

```json
{ "type": "array",
  "minItems": 1,
  "maxItems": 1,
  "items": {
    "type": "object",
    "properties": {
      "total_count": {"type": "integer", "title": "Result count"},
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
}
```

"_id" is unique across the database, while "_key" is only unique within its collection.

### Timestamp parameter

Every method for this API can take a `ts` parameter, representing the Unix
epoch timestamp (in milliseconds) of when the document was active in the
database. This is optional and defaults to the current time.

### taxonomy_re_api.get_taxon(params)

Fetch the document data for a single taxon by ID.

Example request:

```sh
curl -d '{"method": "taxonomy_re_api.get_taxon", "params": [{"id": "ncbi_taxon/100"}]}' <url>
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 1,
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
   }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_associated_ws_objects(params)

Fetch all workspace objects associated with a given taxon.

This endpoint is authorization over workspace objects by passing a KBase token via the `Authorization` header.

Example request:

```sh
curl -d '{"method": "taxonomy_re_api.get_associated_ws_objects", "params": [{"taxon_id": "ncbi_taxon/562"}]}' <url>
curl -X POST -H "Authorization: xyz" <url> \
-d @- << EOF
{
  "method": "taxonomy_re_api.get_associated_ws_objects",
  "params": [{
    "taxon_id": "ncbi_taxon/562"
  }]
}
EOF
```

<details>
<summary>Example response:</summary>
<div>

```json
{
  "version": "1.1",
  "result": [{
    "results": [
      {
        "edge": {
          "_id": "wsfull_obj_version_has_taxon/01ccde39e26cc5f7",
          "assigned_by": "assn1",
          "updated_at": 1565811476862
        },
        "taxon": {
          "_id": "ncbi_taxon/1",
          "rank": "rank1",
          "scientific_name": "sciname1",
          "updated_at": 1565811476636
        }
      },
      {
        "edge": {
          "_id": "wsfull_obj_version_has_taxon/0b9f84ae366ef8e2",
          "assigned_by": "assn2",
          "updated_at": 1565811476862
        },
        "taxon": {
          "_id": "ncbi_taxon/2",
          "rank": "rank2",
          "scientific_name": "sciname2",
          "updated_at": 1565811476637
        }
      }
    ],
    "stats": {
      "executionTime": 0.123,
      "filtered": 0,
      "httpRequests": 0,
      "scannedFull": 0,
      "scannedIndex": 1,
      "writesExecuted": 0,
      "writesIgnored": 0
    }
  }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["taxon_id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "taxon_id": {
      "type": "string",
      "title": "Relation engine document ID of a taxon vertex",
      "examples": ["ncbi_taxon/100"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_lineage(params)

Fetch the ancestors for a taxon vertex.

Example request:

```sh
curl -X POST <url> \
-d @- << EOF
{
  "method": "taxonomy_re_api.get_lineage",
  "params": [{
    "id": "ncbi_taxon/100",
    "limit": 10,
    "offset": 90
  }]
}
EOF
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 9,
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_lineage(params)

Fetch the ancestors for a taxon vertex.

Example request:

```sh
curl -X POST <url> \
-d @- << EOF
{
  "method": "taxonomy_re_api.get_lineage",
  "params": [{
    "id": "ncbi_taxon/100",
    "limit": 10,
    "offset": 90
  }]
}
EOF
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 9,
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_children(params)

Fetch the direct descendants for a taxon vertex.

The optional "search_text" parameter can be specified to search on scientific name for the children.

Within `"search_text"`, you can use this syntax to refine the results:
* Separate search terms by comma: "rhodobacter,pseudomonas"
* To search against a term **OR** another term, use a "|" prefix: "rhodobacter,|pseudomonas"
* To search by prefix, use the "prefix:" prefix: "prefix:rhodo,|prefix:pseudo"
* To exclude a term, use `"-term"`

Example request:

```sh
curl -X POST <url> \
-d @- << EOF
{
  "method": "taxonomy_re_api.get_children",
  "params": [{
    "id": "ncbi_taxon/28211",
    "limit": 3,
    "offset": 180,
    "search_text": ""
  }]
}
EOF
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 21,
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    },
    "search_text": {
      "type": "string",
      "description": "Optional scientific name to search for the children"
    }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.get_siblings(params)

Fetch the siblings for a taxon.

Example request:

```sh
curl -X POST <url> \
-d @- << EOF
{
  "method": "taxonomy_re_api.get_siblings",
  "params": [{
    "id": "ncbi_taxon/100",
    "limit": 3,
    "offset": 10
  }]
}
EOF
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 69,
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["id"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "id": {
      "type": "string",
      "title": "Relation engine document ID",
      "examples": ["ncbi_taxon/100"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    }
  }
}
```

For the response schema, see the **Responses** section above.

### taxonomy_re_api.search_taxa(params)

Search for taxa based on scientific name.

Within `"search_text"`, you can use this syntax to refine the results:
* Separate search terms by comma: "rhodobacter,pseudomonas"
* To search against a term **OR** another term, use a "|" prefix: "rhodobacter,|pseudomonas"
* To search by prefix, use the "prefix:" prefix: "prefix:rhodo,|prefix:pseudo"
* To exclude a term, use `"-term"`

Results are paginated to 20 per page by default. You can pass a `"page"` parameter to get an offset of the results. This parameter defaults to `1`, meaning fetch the first 20 results. Setting "page" to 5 would give you results 101 through 120.

Pass a `"page_len"` param to customize the page length.

Example request:

```sh
curl -d '{"method": "taxonomy_re_api.search_taxa", "params": {"search_text": "prefix:rhodo,|prefix:psuedo"}}' <url>
```

<details>
<summary>Example response:</summary>
<div>

```json
{
    "version": "1.1",
    "result": [{
        "total_count": 4,
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
                "aliases": [],
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
    }]
}
```

</div>
</details>

Request parameters schema (wrapped in an array):

```json
{ "type": "object",
  "required": ["search_text"],
  "properties": {
    "ts": {"type": "integer", "title": "Document timestamp", "description": "Defaults to now."},
    "search_text": {
      "type": "string",
      "title": "Scientific name search query text.",
      "examples": ["prefix:rhodo,|psueodmonas"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 20,
      "maximum": 1000
    },
    "offset": {
      "type": "integer",
      "description": "Number of results to skip",
      "default": 0,
      "maximum": 100000
    }
  }
}
```

For the response schema, see the **Responses** section above.

## Development

Run tests with `make test`
