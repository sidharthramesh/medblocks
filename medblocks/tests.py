from medblocks import scripts, settings
import logging

def test_connections():
    if scripts.check_couch_db():
        logging.info("Successfully got CouchDB instance at {}".format(settings.COUCHDB_URL))

    if scripts.check_rabbit_mq():
        logging.info("Successfully got AMQP instance at {}".format(settings.AMQP_URL))

test_connections()
scripts.check_couch_db_init()