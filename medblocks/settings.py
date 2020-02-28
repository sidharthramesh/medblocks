import logging
from decouple import config
COUCHDB_URL = "http://{}:{}@db:5984".format(config("COUCHDB_USER"), config("COUCHDB_PASSWORD"))
AMQP_URL = "pyamqp://guest:guest@rabbitmq"
CHECK_IP_SERVICE = "https://checkip.amazonaws.com/"
DNS_SERVICE = "8.8.8.8"
S3_URL = "s3:9000"
S3_ACCESS_KEY = config("MINIO_ACCESS_KEY")
S3_SECRET_KEY = config("MINIO_SECRET_KEY")
VERSION = "Medblocks v1"
logging.basicConfig(level=logging.INFO, format="%(asctime)-15s  %(levelname)-8s %(funcName)20s - %(message)s")