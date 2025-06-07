from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any

class KnowledgeBaseRepository:
    def __init__(self, mongo_service):
        self.mongo = mongo_service
        self.collection = self.mongo.db.knowledgebases

    def find_by_id(self, knowledge_base_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma knowledge base pelo ID."""
        return self.collection.find_one({'_id': ObjectId(knowledge_base_id)})

    def update_status(self, knowledge_base_id: str, status: str, error: Optional[str] = None) -> None:
        """Atualiza o status de uma knowledge base."""
        update_data = {
            'status': status,
            'updatedAt': datetime.utcnow()
        }
        
        if error:
            update_data['lastError'] = error
        elif status == 'completed':
            update_data['lastProcessedAt'] = datetime.utcnow()
            
        self.collection.update_one(
            {'_id': ObjectId(knowledge_base_id)},
            {'$set': update_data}
        )

    def update_after_processing(self, knowledge_base_id: str, bucket_file_id: str) -> None:
        """Atualiza a knowledge base após o processamento de um arquivo."""
        self.collection.update_one(
            {'_id': ObjectId(knowledge_base_id)},
            {
                '$set': {
                    'status': 'completed',
                    'updatedAt': datetime.utcnow(),
                    'lastProcessedFile': str(bucket_file_id),
                    'lastProcessedAt': datetime.utcnow()
                }
            }
        ) 