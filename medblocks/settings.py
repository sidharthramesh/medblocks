import logging
# Secret generation and storage in .env 

# Use 
COUCHDB_URL = "http://{}:{}@db:5984".format("admin", "password")
AMQP_URL = "pyamqp://guest:guest@rabbitmq"
CHECK_IP_SERVICE = "https://checkip.amazonaws.com/"
DNS_SERVICE = "8.8.8.8"
S3_URL = "s3:9000"
S3_ACCESS_KEY = "admin"
S3_SECRET_KEY = "password"
# BOOTSTRAP_NODES = []
# OPENPGP_KEYSERVER = ""
VERSION = "Medblocks v1"
logging.basicConfig(level=logging.INFO, format="%(asctime)-15s  %(levelname)-8s %(funcName)20s - %(message)s")