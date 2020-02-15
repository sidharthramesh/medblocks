import json
from nameko.web.handlers import http
from nameko.events import EventDispatcher, event_handler

class HTTPApi:
    """MedBlocks Reference API Implementation 
    https://gitlab.com/medblocks/gomedblocks/-/tree/master/medblocksbackend
    """
    name = "http_api"
    dispatch = EventDispatcher()
    
    @http('GET', '/')
    def get_this(self, request):
        self.dispatch("event_type", "hello!!")
        return 200, "Hello there!"

