#!/usr/bin/env python
# Must be first
import elasticsearch,elasticsearch.helpers
import signal
import sys
import logging
import flask
from flask import Flask


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

# Allow graceful shutdown when using `docker stop`
signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

es_client = elasticsearch.Elasticsearch()
index_name = 'kb-label-lookup'
type_name = 'label-map'


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
    #todo make this json conform to 'article' json spec
    return flask.jsonify(search_results['hits']['hits'])


if __name__ == '__main__':
    app.run(port=5002, host='::', debug=True, use_reloader=False)