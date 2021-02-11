module taxonomy_re_api {

    /*
    Parameters for get_taxon.
        ts - optional - fetch the document with this active timestamp (defaults to now)
        ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        id - required - ID of the taxon node, such as "123"
    */
    typedef structure {
        int ts;
        string ns;
        string id;
    } GetTaxonParams;

    /*
    Parameters for get_lineage.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        id - required - ID of the taxon node, such as "123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string ns;
        string id;
    } GetLineageParams;

    /*
    Parameters for get_children.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        id - required - ID of the taxon node, such as "123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string ns;
        string id;
        int limit;
        int offset;
    } GetChildrenParams;

    /*
    Parameters for get_siblings.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        id - required - ID of the taxon node, such as "123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string ns;
        string id;
        int limit;
        int offset;
    } GetSiblingsParams;

    /*
    Parameters for get_associated_ws_objects.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        search_text - required - scientific name search text
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (deafults to 0)
    */
    typedef structure {
        int ts;
        string ns;
        string search_text;
        int limit;
        int offset;
    } SearchTaxaParams;

    /*
    Parameters for get_associated_ws_objects.
        ts - optional - fetch documents with this active timestamp (defaults to now)
        taxon_ns - required - taxonomy namespace to use (only "ncbi_taxonomy")
        taxon_id - required - ID of the taxon node, such as "123"
        limit - optional - number of results to return (defaults to 20)
        offset - optional - number of results to skip (defaults to 0)
    */
    typedef structure {
        int ts;
        string taxon_id;
        string taxon_ns;
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

    /* get_data_sources definition */
    typedef structure {
        list<string> ns;
    } GetDataSourcesParams;

    typedef structure {
        string url;
        string label;
    } Link;

    typedef structure {
        string url_template;
        string label;
    } TemplateLink;

    /*
        Actually an enum or union of:
        'string' | 'number' | 'boolean' | 'array<string>' | 'array<alias>' | 'array<synonym>' | 'sequence'

    */
    typedef string SourceFieldDataType;

    typedef structure {
        string id;
        SourceFieldDataType type;
        string tooltip;
        string description;
    } SourceFieldDefinition;

    typedef structure {
        string ns;
        string type;
        string title;
        string short_title;
        string data_url;
        string home_url;
        string logo_url;
        Link license;
        TemplateLink item_link;
        string citation;
        list<SourceFieldDefinition> additional_fields;
    } TaxonomySource;

    typedef structure {
        list<TaxonomySource> sources;
    } GetDataSourcesResult;

    /* Get taxonomy data sources */
    funcdef get_data_sources(GetDataSourcesParams params) returns (GetDataSourcesResult result) authentication optional;
};
