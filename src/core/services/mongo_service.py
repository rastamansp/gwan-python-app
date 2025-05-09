from pymongo import MongoClient

class MongoService:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
    # Adicione métodos conforme necessário 