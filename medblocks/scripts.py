from nameko.runners import ServiceRunner
from medblocks.http import HTTPApi
from medblocks.workers import DatabaseService, BlobDataService, RelayService
from medblocks import settings
import time
import requests
import logging
import socket
from kombu import Connection

def check_couch_db():
    for attempt in range(1, 11):
        timeout = attempt * 3
        try:
            r = requests.get(settings.COUCHDB_URL).json()
            assert r["couchdb"] == "Welcome"
            return True
        except requests.ConnectTimeout:
            logging.error("CouchDB timed out. Retrying in {} secs...".format(timeout))  
            time.sleep(timeout)  
        except requests.ConnectionError:
            logging.error("Cannot connect to CouchDB host at {}. Please ensure service is running. Retrying in {} secs...".format(settings.COUCHDB_URL, timeout))
            time.sleep(timeout)
    return False

def check_couch_db_init():
    baseUrl = settings.COUCHDB_URL + "/{}"
    # iptable init
    iptable_resp = requests.get(baseUrl.format("iptable")).json()
    try:
        if iptable_resp["db_name"] == "iptable":
            logging.info("Found existing iptable database")
    except KeyError:
        if iptable_resp["error"] == "not_found":
            logging.info("No iptable database found")

     
def init_couch_db():

    read_only_doc = '''{
        "_id": "_design/readonly",
        "validate_doc_update": "function(newDoc, oldDoc, userCtx, secObj) {throw({forbidden: 'This transaction is read only'});}"
    }'''

def check_rabbit_mq():
    conn = Connection(settings.AMQP_URL)
    for attempt in range(1, 11):
        timeout = attempt * 3
        try:
            conn.connect()
            # Check connection
            conn.release()
            return True
        except OSError as e:
            logging.error("Cannot connect to AMQP at {}. Error message: OSError: {}. Retrying in {} secs...".format(settings.AMQP_URL, e, timeout))  
            time.sleep(timeout)
    return False
    

def check_blob_storage():
    pass

def check_ip_address() -> (str, str):
    """checks for internal and external ip address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((settings.DNS_SERVICE, 80))
    internal_ip_address = s.getsockname()[0]
    s.close()

    external_ip_address = requests.get(settings.CHECK_IP_SERVICE).text.strip()
    return internal_ip_address, external_ip_address

def initialize():
    # Do all dependancy checks
    # Set up migrations
    import eventlet

    eventlet.monkey_patch()
    runner = ServiceRunner(config={"AMQP_URI": settings.AMQP_URL})
    runner.add_service()