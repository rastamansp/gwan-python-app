from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any

class BucketFileRepository:
    def __init__(self, mongo_service):
        self.mongo = mongo_service
        self.collection = self.mongo.db.bucketfiles

    def find_by_id(self, bucket_file_id: str) -> Optional[Dict[str, Any]]:
        """Busca um arquivo do bucket pelo ID."""
        return self.collection.find_one({'_id': ObjectId(bucket_file_id)})

    def update_processing_status(self, bucket_file_id: str, status: str, error: Optional[str] = None, 
                               markdown_path: Optional[str] = None, total_chunks: Optional[int] = None) -> None:
        """Atualiza o status de processamento de um arquivo."""
        update_data = {
            'status': status,
            'updatedAt': datetime.utcnow()
        }
        
        if error:
            update_data['error'] = error
        elif status == 'completed':
            update_data.update({
                'markdownPath': markdown_path,
                'embeddingsStored': True,
                'totalChunks': total_chunks
            })
            
        self.collection.update_one(
            {'_id': ObjectId(bucket_file_id)},
            {'$set': update_data}
        ) 