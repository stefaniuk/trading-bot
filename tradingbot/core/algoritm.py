class Pivot(object):
    def __init__(self, api, conf):
        self.api = api
        self.conf = conf
        self.graph = Grapher(self.conf)