module taxonomy_re_api {

    /*
    Parameters for get_taxon.
        ts - optional - fetch the document with this active timestamp (defaults to now)
        id - required - ID of the taxon node, such as "ncbi_taxon/123"
    */
    typedef structure {
        int ts;
        string id;
    } GetTaxonParams;

    /*
    Parameters for get_lineage.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        id - required - ID of the taxon node, such as "ncbi_taxon/123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string id;
    } GetLineageParams;

    /*
    Parameters for get_children.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        id - required - ID of the taxon node, such as "ncbi_taxon/123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string id;
        int limit;
        int offset;
    } GetChildrenParams;

    /*
    Parameters for get_siblings.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        id - required - ID of the taxon node, such as "ncbi_taxon/123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string id;
        int limit;
        int offset;
    } GetSiblingsParams;

    /*
    Parameters for get_associated_ws_objects.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        search_text - required - scientific name search text
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (deafults to 0)
    */
    typedef structure {
        int ts;
        string search_text;
        int limit;
        int offset;
    } SearchTaxaParams;

    /*
    Parameters for get_associated_ws_objects.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        taxon_id - required - ID of the taxon node, such as "ncbi_taxon/123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string taxon_id;
        int limit;
        int offset;
    } GetAssociatedWsObjectsParams;

    /*
    Generic results for each method.
        stats - Query execution information from ArangoDB.
        results - array of objects of results.
    */
    typedef structure {
        UnspecifiedObject stats;
        list<UnspecifiedObject> results;
    } Results;

    /* Fetch details of a taxon by ID. */
    funcdef get_taxon(GetTaxonParams params) returns (Results result);

    /* Fetch the ancestors of a taxon by ID, in order of root node to leaf node. */
    funcdef get_lineage(GetLineageParams params) returns (Results result);

    /* Fetch the children of a taxon by ID. */
    funcdef get_children(GetChildrenParams params) returns (Results result);

    /* Fetch the siblings of a taxon by ID. */
    funcdef get_siblings(GetSiblingsParams params) returns (Results result);

    /* Search all taxon nodes by scientific name. */
    funcdef search_taxa(SearchTaxaParams params) returns (Results result);

    /* Get all workspace objects associated with a taxon. */
    funcdef get_associated_ws_objects(GetAssociatedWsObjectsParams params)
        returns (Results results) authentication optional;
};
