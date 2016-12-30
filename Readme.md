# Custom Knowledgebase Yodaqa Label-Lookup Service
 
 Flask backend for the label-lookup api conforming to interface provided by https://github.com/brmson/label-lookup
 
 Motivation is to provide a label-lookup service for a custom knowledge base, in hopes of integrating into yodaqa pipeline.
 The existing yodaqa label-lookup services are tightly coupled with dbpedia/wikipedia articles. 
 
 Instead of writing our own fuzzy search algorithm, we use Elasticsearch's fuzzy query api, assuming that all of our rdf triples' labels and their corresponding uris have been indexed in ES. (See my rdf-label-indexer repo).
  
 Hopefully we can also leverage the "score" field returned by ES into yoda.