#!/usr/bin/env python

import elasticsearch, elasticsearch.helpers
import signal
import sys
import logging
import flask
import editdistance
from flask import Flask

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

# Allow graceful shutdown when using `docker stop`
signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

es_client = elasticsearch.Elasticsearch()
index_name = 'kb-label-lookup'
type_name = 'label-map'


def flask_result_to_article_schema(elastic_result, search_query):
    elastic_hit = elastic_result['_source']
    return {
        'matchedLabel': elastic_hit['label'],
        'canonLabel': elastic_hit['canonical_label'],
        'prob': '0',  # todo change this after understanding probabilty's impact in pipeline
        'dist': editdistance.eval(search_query.lower(), elastic_hit['label'].lower()),
        'name': elastic_hit['label'],  # todo investigate how yodaqa uses name
        'pop': elastic_result['_score'],
        'description': elastic_hit['description']
    }


# Due to how flask handles slashes
# https://github.com/pallets/flask/issues/900
# https://github.com/flask-restful/flask-restful/issues/393
# we ask for the search term to be a querystring parameter 'name' instead of directly part of the route

@app.route('/search')
def search():
    name = flask.request.args.get('name')
    logger.info('searching ' + name.encode('utf-8'))
    search_results = es_client.search(index=[index_name], doc_type=[type_name], track_scores=True, body={
        "query": {
            "match": {
                "label": {
                    "query": name,
                    "fuzziness": "AUTO"
                }
            }
        }
    })
    return flask.jsonify({'results': [flask_result_to_article_schema(result,name) for result in search_results['hits']['hits']]})


if __name__ == '__main__':
    app.run(port=5002, host='::', debug=True, use_reloader=False)
