class DuplicateKey(Exception):
    """The code is already in use"""


class Storage:
    def __init__(self):
        self.storage = {}

    def put(self, key, data):
        if key in self.storage:
            raise DuplicateKey
        self.storage[key] = data
        return key

    def get(self, key):
        return self.storage.get(key)
