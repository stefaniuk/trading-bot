import os.path
import yaml


class Configurer(object):
    def __init__(self, path):
        self.config_file = path
        self.config = {}

    def read(self):
        with open(self.config_file, 'r') as f:
            self.config = yaml.load(f)

    def save(self):
        if not self.config:
            raise Exception("nothing to save (config not exists)")
        with open(self.config_file, 'w') as f:
            f.write(yaml.dump(self.config))

    def checkFile(self):
        if os.path.isfile(self.config_file):
            return 1
        else:
            return 0
