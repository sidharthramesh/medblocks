import json
from nameko.web.handlers import http
from nameko.events import EventDispatcher, event_handler
import logging

class LogService:
    name = "log_service"
    @event_handler("http_service", "event_type")
    def print_result(self, payload):
        logging.info("Got it {}".format(payload))

class DatabaseService:
    # 2 way Replications from iptable
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
    def dbChanges(self):
        """Listen on the _changes"""
        # Changes on data to BlobDataService dataUploader
        
        # Listen to activity/_changes to setupReplications if IP address has good ping 

        # Trigger event
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
    def dataUploadWorker(self):
        # Look at attachments in data database
        # Upload to S3
        # Make update to document: - detele attachment and set uploaded: true
        pass