import os.path
import codecs
import yaml


class Configurer(object):
    def __init__(self, path):
        self.config_file = path
        self.config = {}

    def read(self):
        with codecs.open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.load(f)

    def save(self):
        if not self.config:
            raise Exception("nothing to save (config not exists)")
        with codecs.open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(yaml.dump(self.config))

    def checkFile(self):
        if os.path.isfile(self.config_file):
            return 1
        else:
            return 0
