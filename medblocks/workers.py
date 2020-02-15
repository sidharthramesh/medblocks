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
    # Set up transaction store
    # Set up iptable
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
    pass

class BlobDataService:
    # Create public bucket per user
    # Get encrypted data for all medblocks and store
    # Sync occasionally
    pass

class RelayService:
    # Send new updates to connected servers
    # Send 
    pass