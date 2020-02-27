import json
from medblocks import settings
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.web.handlers import http
from nameko.events import EventDispatcher, event_handler
from nameko.timer import timer
import logging
import requests
class HttpServer:
    name = "http_service"
    @http("GET", "/")
    def version(self, request):
        return json.dumps({"version": "Medblocks v1"})

class DatabaseService:
    # 2 way Replications from iptable
    name = "sync_service"
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
    @timer(interval=1)
    def dataChanges(self):
        """Listen on the _changes"""
        # Changes on data to BlobDataService dataUploader
        db = "data"
        localdb = "medblocksSync"
        last_seq = requests.get(f"{settings.COUCHDB_URL}/{db}/_local/{localdb}").json()
        if last_seq["error"]:
            last_seq = None
        else:
            last_seq = last_seq["last_seq"]
        if last_seq is not None:
            url = f"{settings.COUCHDB_URL}/{db}/_changes?since={last_seq}"
        else:
            url = "http://db:5984/data/_changes"
        changes = requests.get(url).json()
        for change in changes:
            seq = change["seq"]
            id = change["id"]
        with ClusterRpcProxy(config={"AMQP_URI": settings.AMQP_URL}):
            # Async call to minio service with id
            result = pass
            pass
        r = requests.put(f"{settings.COUCHDB_URL}/{db}/_local/{localdb}", json={"last_seq":seq})

        print(changes["last_seq"])
        
        print(r.json())
    
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
    def dataUploadWorker(self, id):
        # Look at attachments in data database
        # Upload to S3
        # Make update to document: - detele attachment and set uploaded: true
        pass