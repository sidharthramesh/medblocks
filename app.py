import json
from nameko.web.handlers import http
from nameko.events import EventDispatcher, event_handler
import logging

class HttpService:
    name = "service_a"
    dispatch = EventDispatcher()
    @http('GET', '/')
    def get_this(self, request):
        self.dispatch("event_type", "hello!!")
        return 200, "Hello there!"

class PrintService:
    name = "print_service"

    @event_handler("service_a", "event_type")
    def print_result(self, payload):
        logging.info("Got it {}".format(payload))
