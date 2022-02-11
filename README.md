# nuxeo_index_sync

Sometimes the nuxeo database and elasticsearch index can get out of sync for whatever reason. This is an issue because the web UI depends on es for searching. It is also a problem because the new Nuxeo API endpoints use elasticsearch rather than the database. So we really want elasticsearch to be in sync with the database.

To resolve this:

## run a full reindex of nuxeo 
See the [Nuxeo reindex documentation](https://doc.nuxeo.com/nxdoc/elasticsearch-setup/#rebuilding-the-repository-index)

### Notes from Feb 2022

We ran it in the browser using the `SF UI > Admin center > Elasticsearch > Admin` interface.

We needed to temporarily increase the size of our AWS OpenSearch cluster instance types while running the reindex. This was necessary because with the regular `t3.small.search` instance we were using, we were getting `429 slow down` errors from ElasticSearch. Memory and disk size were fine, so we just upped the instance size to `m5.xlarge.search`, which has 4 vCPUs rather than 2 vCPUs.

We still got some errors from reindexing like this:

> org.nuxeo.ecm.core.api.DocumentNotFoundException: Unknown document type: nxtrSamplesContainer

and 

> 2022-02-08T22:16:41,287 ERROR [Nuxeo-Work-elasticSearchIndexing-1095] [org.nuxeo.ecm.core.work.WorkManagerImpl] Uncaught error on thread: Nuxeo-Work-elasticSearchIndexing-1095, current work might be lost, WorkManager metrics might be corrupted.
org.nuxeo.ecm.core.api.NuxeoException: Work failed after 1 retry, class=class org.nuxeo.elasticsearch.work.BucketIndexingWorker id=758511973539799.1167467553 category=elasticSearchIndexing title= ElasticSearch bucket indexer size 250

which I think explains why there were still hundreds of records missing from elasticsearch after the reindex (see below).


## run the nuxeo esync tool

Run the [Nuxeo esync tool](https://github.com/nuxeo/esync) to compare database and elasticsearch content.

This has to be run on a machine that has access to both the database and elasticsearch.

Capture the output in a txt file, which will be used by the scripts described below.

See `nuxeo-esync-20220209.txt` for the example output.

## run scripts to get still missing records into elasticsearch

Sort of a hacky workaround to trigger an elasticsearch index of the records that got skipped by the full reindex. This way we don't have to actually work figure out the index rebuild errors in code we didn't write %-)

### install python packages

`$ pip install -r requirements.txt`
`$ pip install https://github.com/ucldc/pynux/tarball/master --upgrade`

### create a list of records to be updated based on the output from the esync tool

`$ python list_missing_paths.py`

### trigger an elasticsearch index of each of those records

`$ python update_es.py`

### check to see which records are still missing

`$ check_es.py`

#### Notes from Feb 2022

There were a few records that still couldn't be created in elasticsearch, but these were all "archived" docs or duplicate docs where there are 2 records in the database with the same path, and one of those is in elasticsearch. So I think we're basically all synced up.