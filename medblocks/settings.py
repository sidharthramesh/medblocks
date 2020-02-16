import logging

COUCHDB_URL = "http://db:5984"
AMQP_URL = "pyamqp://guest:guest@rabbitmq"
CHECK_IP_SERVICE = "https://checkip.amazonaws.com/"
DNS_SERVICE = "8.8.8.8"

logging.basicConfig(level=logging.INFO, format="[%(asctime)-15s  %(levelname)-8s %(funcName)20s - %(message)s")