import os
from nuxeo.client import Nuxeo
import json

API_BASE = 'https://nuxeo.cdlib.org/Nuxeo/site'
API_PATH = 'api/v1'
NUXEO_PASSWORD = os.environ.get('NUXEO_PASS')

'''
    reads in a json file such as the one created by list_missing_paths.py
    
    outputs a json file `still_missing.json` that lists docs still missing
    from the elasticsearch index
'''
with open('all_missing_20220211.json', 'r') as f:
    missing = json.load(f)

#trashed = [m for m in missing if 'trashed' in m['path']]

nuxeo = Nuxeo(
    auth=('Administrator', NUXEO_PASSWORD),
    host=API_BASE,
    api_path=API_PATH
)

still_missing = []
for doc in missing:
    NXQL = f"SELECT * FROM Document WHERE ecm:uuid = '{doc['uid']}'"
    response = nuxeo.documents.query(opts={'query': NXQL})
    if not doc['path'].startswith('/default-domain/workspaces/templatesamples/') \
    and not doc['path'].startswith('/asset-library/UCOP/Aggie') \
    and doc['path'] != '/default-domain/UserWorkspaces/barrett-ucsc-edu' \
    and not doc['path'].startswith('/asset-library/workspaces/Nuxeo Marketing Content') \
    and not doc['path'].startswith('/asset-library/UCM/Aggie') \
    and not doc['path'].startswith('/asset-library/UCSB/Aggie') \
    and not 'trashed' in doc['path'] \
    and len(response['entries']) == 0:
        still_missing.append(doc)

with open('still_missing.json', 'w') as f:
    f.write(json.dumps(still_missing))

print(f"total still missing from elasticsearch: {len(still_missing)}")