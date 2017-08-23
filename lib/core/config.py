import configparser
import os

class Configurer(object):
    def __init__(self, name="data.ini"):
        self.config = configparser.ConfigParser()
        self.config_file = self._combine(name)

    def _combine(self, path):
        return os.path.join(os.path.dirname(__file__), path)

    def addLogin(self, username, password):
        self.config['TRADING212'] = {'username': username,
                                     'password': password}
        with open(self.config_file, 'w') as cf:
            self.config.write(cf)

    def read(self):
        self.config.read(self.config_file)

    def checkFile(self):
        if os.path.isfile(self._combine(self.config_file)):
            return 1
        else:
            return 0