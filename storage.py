from datetime import datetime


class DuplicateKey(Exception):
    """The shortcode is already in use"""


class Storage:
    """I leave it to reviewers to """

    def __init__(self):
        self.storage = {}
        self.stats = {}

    def put(self, key, data):
        if key in self.storage:
            raise DuplicateKey
        self.storage[key] = data
        self.stats[key] = {
            "created": datetime.now(),
            "lastRedirect": None,
            "redirectCount": 0,
        }
        return key

    def get(self, key):
        if key not in self.storage:
            return None
        value = self.storage[key]
        self.stats[key]["redirectCount"] += 1
        self.stats[key]["lastRedirect"] = datetime.now()
        return value

    def get_stats(self, key):
        return self.stats.get(key)
