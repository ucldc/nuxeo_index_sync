import sys, os
from os.path import expanduser
from pynux import utils
import requests
import json
from datetime import datetime

PYNUXRC = os.environ.get('PYNUXRC')

''' reads in the output of the nuxeo esync tool: https://github.com/nuxeo/esync 
    outputs a json file with uid, path, and title of documents that esync reported missing from elasticsearch
'''
with open('nuxeo-esync-20220209.txt') as f:
    missing = [{'uid': line.split()[4][:-1], 'type': line.split()[6]} for line in f if line.split()[2] == '[MissingListener]']

print(f"number of missing records {len(missing)}")

nx = utils.Nuxeo(rcfile=open(expanduser(PYNUXRC), 'r'))

now = datetime.now()
datestring = now.strftime("%Y%m%d")

for m in missing:
    try:
        metadata = nx.get_metadata(uid=m['uid'])
    except requests.exceptions.HTTPError:
        path = "NONE"
    m['path'] = metadata['path']
    m['dc:title'] = metadata['properties']['dc:title']

with open(f"all_missing_{datestring}.json", 'w') as f:
    f.write(json.dumps(missing))

