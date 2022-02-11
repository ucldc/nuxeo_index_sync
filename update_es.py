import os
from pynux import utils
import json
import urllib3
import requests

PYNUXRC = os.environ.get('PYNUXRC')

'''
    reads in a json file 
    can use the one created by `list_missing_paths.py`
    OR
    the one created by check_es.py

    trigger an elasticsearch index update for each doc by using pynux 
    to fake "update" the metadata for each doc.

    pynux uses the nuxeo API endpoint that hits the database
    rather than elasticsearch, so we can retrieve each doc, update it,
    and then that triggers an elasticsearch update.

    there are some records that have 2 or more entries in the database
    for the same path. This causes 404 errors when doing `pynux.get_metadata`
    or 500 errors when doing `pynux.update_nuxeo_properties`.
'''
with open('still_missing.json', 'r') as f:
    missing = json.load(f)

docs = missing
#docs = [m for m in missing if 'trashed' not in m['path'] and m['path'] != 'NONE']

print(f"Num of docs to update: {len(docs)}")
print("------------------------------")

pynux = utils.Nuxeo(rcfile=open(PYNUXRC, 'r'))

retry_errors = []
http_errors = []
docs_updated = 0
http_error_count = 0
retry_error_count = 0
for doc in docs:
    uid = doc['uid']
    try:
        metadata = pynux.get_metadata(uid=uid)
    except requests.exceptions.HTTPError as exception:
        doc['HTTPError'] = str(exception)
        http_errors.append(doc)
        http_error_count = http_error_count + 1
    else:
        try:
            pynux.update_nuxeo_properties(metadata, uid=uid)
        except requests.exceptions.RetryError as exception:
            doc['RetryError'] = str(exception)
            retry_errors.append(doc)
            retry_error_count = retry_error_count + 1
        else:
            docs_updated = docs_updated + 1
            print(f"touched {uid} {metadata['path']}")

print(f"Number of docs updated: {docs_updated}")
print(f"Number of http errors: {http_error_count}")
print(f"Number of retry errors: {retry_error_count}")
print(f"Total: {docs_updated + http_error_count + retry_error_count}")

with open('retry_errors.json', 'w') as f:
    f.write(json.dumps(retry_errors))

with open('http_errors.json', 'w') as f:
    f.write(json.dumps(http_errors))