from nameko.runners import ServiceRunner
from http import HTTPApi
from workers import DatabaseService, BlobDataService, RelayService


def check_couch_db():
    pass

def init_couch_db():


    read_only_doc = '''{
        "_id": "_design/readonly",
        "validate_doc_update": "function(newDoc, oldDoc, userCtx, secObj) {throw({forbidden: 'This transaction is read only'});}"
    }'''

def check_rabbit_mq():
    pass

def initialize():
    # Do all dependancy checks
    # Set up migrations
    import eventlet

    eventlet.monkey_patch()
    runner = ServiceRunner(config={"AMQP_URI":"pyamqp://guest:guest@rabbitmq"})
    runner.add_service()