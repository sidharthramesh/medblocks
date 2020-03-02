import json
from medblocks import settings
from medblocks.entrypoints import cors_http as http
from nameko.events import EventDispatcher, event_handler
from nameko.timer import timer
from nameko.rpc import rpc, RpcProxy
import minio
import io
import logging
import requests
class HttpServer:
    name = "http_service"
    @http("GET", "/")
    def version(self, request):
        return json.dumps({"version": settings.VERSION})
    @http("GET", "/replication")
    def get_replications(self, requests):
        pass
    @http("POST", "/replication")
    def setup_replication(self, request):
        replication_doc = '''{
        "_id": "{id}",
        "source": "{source}",
        "target": "{target}",
        "create_target": false,
        "continuous": true,
        "selector": {
        "$not": {
            "_id": "_design/readonly"
            }
            }
        }'''

        pass
class DatabaseService:
    # 2 way Replications from iptable
    name = "sync_service"
    
    blob_data_service = RpcProxy("blob_data_service")
    @timer(interval=1)
    def dataChanges(self):
        """Listen on the _changes"""
        # Changes on data to BlobDataService dataUploader
        db = "data"
        localdb = "medblocksSync"
        last_seq = requests.get(f"{settings.COUCHDB_URL}/{db}/_local/{localdb}").json()
        try:
            last_seq = last_seq["last_seq"]
            logging.debug(f"Got last_seq: {last_seq}")
        except KeyError:
            logging.debug("Did not get last_seq from _local")
            last_seq = None
        if last_seq is not None:
            url = f"{settings.COUCHDB_URL}/{db}/_changes?since={last_seq}"
        else:
            url = f"{settings.COUCHDB_URL}/{db}/_changes"
        changes = requests.get(url).json()["results"]
        if len(changes) > 0:
            results = []
            seqs = []
            deleted = []
            for change in changes:
                seq = change["seq"]
                seqs.append(seq)
                if change.get("deleted"):
                    continue
                id = change["id"]
                logging.info(f"Change found for data: {id}")
                logging.debug(f"Triggering upload to s3 for {id}")
                res = self.blob_data_service.dataUpload.call_async(id)
                results.append(res)
            seq_dict = {int(seq.split("-")[0]):seq for seq in seqs}
            sorted_seq = sorted(seq_dict)
            logging.info(sorted_seq)
            # Assert if continuous sequence
            assert all(a+1==b for a, b in zip(sorted_seq, sorted_seq[1:])), "Sorted sequence not continuous"
            last_seq = seq_dict[sorted_seq[-1]]
            # Wait for all results to complete
            results = [res.result() for res in results]
            if all(results):
                r = requests.put(f"{settings.COUCHDB_URL}/{db}/_local/{localdb}", json={"last_seq":last_seq})

    
    def txChanges(self):
        pass
    def activityChanges(self):
        pass
    def activityScan(self):
        """Scan all IP addresses in activity and trigger replication"""

        # Trigger event
        pass
    def setupReplications(self, ipAddress):
        """Set up replications"""
        # Exculde localhost, 127.0.0.1 etc
        # Check and establish connection
        # Set up 2 way reaplication for activity and tx databases
        pass


class BlobDataService:
    name = "blob_data_service"
    @rpc
    def dataUpload(self, id):
        try:
            # Look at attachments in data database
            r = requests.get(f"{settings.COUCHDB_URL}/data/{id}/file")
            data = io.BytesIO(r.content)
            # Upload to S3
            client = minio.Minio(settings.S3_URL, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, secure=False)
            res = client.put_object("blob", id, data, length=len(r.content))
            assert type(res) == str, "Minio response to put not string"
            rev = requests.get(f"{settings.COUCHDB_URL}/data/{id}").json()["_rev"]
            # Make update to document: - detele attachment
            logging.info(f"Uploaded {id} to S3")
            r = requests.delete(f"{settings.COUCHDB_URL}/data/{id}", params={"rev":rev})
            assert r.status_code == 200, "Delete status code not 200"
            return True
        except AssertionError as e:
            logging.error(f"id: {id} encountered error:{e}")
            return False
        except Exception as e:
            raise e

    @rpc
    def sleep(self, name):
        from time import sleep
        sleep(5)
        return name
        # Verify s3 upload