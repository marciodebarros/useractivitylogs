import asyncio
from app.config import Configuration
from goblin import Goblin

class JanusGraphConnection(object):
    class __JanusGraphConnection:
        def __init__(self):
            loop = asyncio.get_event_loop()
            self.val = Goblin.open(loop,
                                   hosts=[Configuration.JANUSGRAPH_DB_SERVER],
                                   port=Configuration.JANUSGRAPH_DB_PORT,
                                   scheme=Configuration.JANUSGRAPH_DB_SCHEMA)
        def __str__(self):
            return self.val
    instance = None
    def __new__(cls): # __new__ always a classmethod
        if not JanusGraphConnection.instance:
            JanusGraphConnection.instance = JanusGraphConnection.__JanusGraphConnection()
        return JanusGraphConnection.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)