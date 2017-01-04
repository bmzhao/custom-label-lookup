#!/usr/bin/env python
# Must be first
import elasticsearch,elasticsearch.helpers
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


def flask_result_to_article_schema(flask_result, search_query):
    flask_result = flask_result['_source']
    return {
        'matchedLabel': flask_result['label'],
        'canonLabel': flask_result['canonical_label'],
        'prob': '0', #todo change this after understanding probabilty's impact in pipeline
        'dist': editdistance.eval(search_query.lower(),flask_result['label'].lower()),
        'name': flask_result['label'], #todo investigate how yodaqa uses name
    }



@app.route('/search/<name>')
def search(name):
    logger.info('searching ' + name.encode('utf-8'))
    search_results = es_client.search(index=[index_name],doc_type=[type_name],track_scores=True,body={
        "query": {
            "match": {
                "label": {
                    "query":     name,
                    "fuzziness": "AUTO"
                }
            }
        }
    })
    return flask.jsonify({'results': [flask_result_to_article_schema(result,name) for result in search_results['hits']['hits']]})


if __name__ == '__main__':
    app.run(port=5002, host='::', debug=True, use_reloader=False)