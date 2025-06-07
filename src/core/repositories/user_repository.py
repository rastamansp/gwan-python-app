from bson import ObjectId
from typing import Optional, Dict, Any

class UserRepository:
    def __init__(self, mongo_service):
        self.mongo = mongo_service
        self.collection = self.mongo.db.users

    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo ID."""
        return self.collection.find_one({'_id': ObjectId(user_id)}) 