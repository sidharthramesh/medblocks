from medblocks import settings
import time
import requests
import logging
import socket
from kombu import Connection
from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
import json
def check_couch_db():
    for attempt in range(1, 11):
        timeout = attempt * 2
        try:
            r = requests.get(settings.COUCHDB_URL).json()
            assert r["couchdb"] == "Welcome"
            return True
        except requests.ConnectTimeout:
            logging.warning("CouchDB timed out. Retrying in {} secs...".format(timeout))  
            time.sleep(timeout)
        except requests.ConnectionError:
            logging.warning("Cannot connect to CouchDB host at {}. Please ensure service is running. Retrying in {} secs...".format(settings.COUCHDB_URL, timeout))
            time.sleep(timeout)
    return False

def check_couch_db_init():
    baseUrl = settings.COUCHDB_URL + "/{}"
    read_only_doc = {
        "_id": "_design/readonly",
        "validate_doc_update": "function(newDoc, oldDoc, userCtx, secObj) {if (oldDoc !== null) {throw({forbidden: 'This transaction is read only'});};}"
    }
    hashTypeToIndex = {
            "_id": "_design/hashTypeToIndex",
            "language": "query",
            "views": {
                "hashTypeToIndex": {
                "map": {
                    "fields": {
                    "hash": "asc",
                    "type": "asc",
                    "to": "asc"
                    },
                    "partial_filter_selector": {}
                },
                "reduce": "_count",
                "options": {
                    "def": {
                    "fields": [
                        "hash",
                        "type",
                        "to"
                    ]
                    }
                }
                }
            }
            }
    toTypeTagIndex = {
            "_id": "_design/toTypeTagIndex",
            "language": "query",
            "views": {
                "toType": {
                "map": {
                    "fields": {
                    "to": "asc",
                    "type": "asc",
                    "tag": "asc"
                    },
                    "partial_filter_selector": {}
                },
                "reduce": "_count",
                "options": {
                    "def": {
                    "fields": [
                        "to",
                        "type",
                        "tag"
                    ]
                    }
                }
                }
            }
            }
    emailTypeTimeIndex = {
            "_id": "_design/emailTypeTime",
            "language": "query",
            "views": {
                "emailTypeTime": {
                "map": {
                    "fields": {
                    "email": "asc",
                    "type": "asc",
                    "time": "asc"
                    },
                    "partial_filter_selector": {}
                },
                "reduce": "_count",
                "options": {
                    "def": {
                    "fields": [
                        "email",
                        "type",
                        "time"
                    ]
                    }
                }
                }
            }
            }
    database_documents = {
        "activity": [read_only_doc, emailTypeTimeIndex],
        "tx": [read_only_doc, hashTypeToIndex, toTypeTagIndex],
        "data": []
    }
    cors = {
        "_node/nonode@nohost/_config/httpd/enable_cors": "true",
        "_node/nonode@nohost/_config/cors/origins": "*",
        "_node/nonode@nohost/_config/cors/methods": "GET, PUT, POST, HEAD, DELETE",
        "_node/nonode@nohost/_config/cors/headers": "accept, authorization, content-type, origin, referer, x-csrf-token",
        "_node/nonode@nohost/_config/cors/credentials": "true",
        "_node/nonode@nohost/_config/vendor/name": settings.VERSION
    }

    logging.info("Enabling CORS")
    for url,data in cors.items():
        r = requests.put(baseUrl.format(url), json=data)
        if not r.status_code == 200:
            logging.error(f"Setting CORS failed for {url}")

    for db in database_documents.keys():
        db_resp = requests.get(baseUrl.format(db)).json()
        try:
            if db_resp["db_name"] == db:
                logging.info("Found existing {} database".format(db))
        except KeyError:
            if db_resp["error"] == "not_found":
                logging.info("No {} database found".format(db))
                r = requests.put(baseUrl.format(db)).json()
                try:
                    database_created = r["ok"]
                    if database_created:
                        logging.info("Created {} database".format(db))
                        design_docs = database_documents[db]
                        for design_doc in design_docs:
                            doc_id = design_doc["_id"]
                            r = requests.put(baseUrl.format(db)+"/"+doc_id, json=design_doc).json()
                            logging.debug(r)
                            try:
                                design_doc_created = r["ok"]
                                if design_doc_created:
                                    logging.info(f"Created {doc_id} design document at {db}")
                            except KeyError:
                                logging.error(f"Design doc {doc_id} could not be created at {db}")
                        
                except KeyError:
                    logging.error("Database {} could not be created".format(db))
                
        
def check_rabbit_mq():
    conn = Connection(settings.AMQP_URL)
    for attempt in range(1, 11):
        timeout = attempt * 2
        try:
            conn.connect()
            # Check connection
            conn.release()
            return True
        except OSError as e:
            logging.warning("Cannot connect to AMQP at {}. Retrying in {} secs...".format(settings.AMQP_URL, timeout))  
            time.sleep(timeout)
    return False
    

def check_blob_storage():
    # Init public bucket
    logging.info("Establishing connection to Object Storage")
    for attempt in range(1, 11):
        timeout = attempt * 2
        try:
            minioClient = Minio(settings.S3_URL,
                        access_key=settings.S3_ACCESS_KEY,
                        secret_key=settings.S3_SECRET_KEY,
                        secure=False)
        except ConnectionRefusedError:
            logging.warning(f"Cannot connect to S3 at {settings.S3_URL}. Retrying in {timeout} secs...")
            time.sleep(timeout)
    try:
        logging.info("Creating bucket blob")
        minioClient.make_bucket("blob")
        policy_read_only = {
        "Version":"2012-10-17",
        "Statement":[
            {
            "Sid":"",
            "Effect":"Allow",
            "Principal":{"AWS":"*"},
            "Action":"s3:GetBucketLocation",
            "Resource":"arn:aws:s3:::blob"
            },
            {
            "Sid":"",
            "Effect":"Allow",
            "Principal":{"AWS":"*"},
            "Action":"s3:ListBucket",
            "Resource":"arn:aws:s3:::blob"
            },
            {
            "Sid":"",
            "Effect":"Allow",
            "Principal":{"AWS":"*"},
            "Action":"s3:GetObject",
            "Resource":"arn:aws:s3:::blob/*"
            }
        ]
        }
        logging.info("Setting bucket policy as public")
        minioClient.set_bucket_policy("blob", json.dumps(policy_read_only))
    except BucketAlreadyOwnedByYou as err:
        logging.info("Bucket blob already exists")
    except BucketAlreadyExists as err:
        logging.info("Bucket blob already exists")
    except ResponseError as err:
        raise err
    
def test_connections():
    logging.info("Establishing connection to CouchDB instance")
    if check_couch_db():
        logging.info("Successfully got CouchDB instance at {}".format(settings.COUCHDB_URL))
    logging.info("Establishing connection to AMQP instance")
    if check_rabbit_mq():
        logging.info("Successfully got AMQP instance at {}".format(settings.AMQP_URL))
    if check_blob_storage():
        logging.info("Successfully got S3 instance at {}".format(settings.S3_URL))
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
    logging.info(f"Initializing {settings.VERSION}")
    test_connections()
    logging.info("Initializing CouchDB database and design documents")
    check_couch_db_init()
    return True