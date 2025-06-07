from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from src.database.config import Base
import numpy as np
from typing import Optional, Dict, Any
import json

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    knowledgeBaseId = Column(String, nullable=False, index=True, name="knowledge_base_id")
    userId = Column(String, nullable=False, index=True, name="user_id")
    bucketFileId = Column(String, nullable=False, index=True, name="bucket_file_id")
    chunkIndex = Column(Integer, nullable=False, name="chunk_index")
    content = Column(Text, nullable=False, name="content")
    embedding = Column(Text, nullable=False, name="embedding")  # Armazenado como string JSON (vetor de 1536 dimensões)
    meta = Column(JSON, nullable=True, name="meta")  # (metadata opcional com tokenCount, pageNumber, section)

    def __init__(self, knowledgeBaseId: str, userId: str, bucketFileId: str, chunkIndex: int, content: str, embedding: np.ndarray, meta: Optional[Dict[str, Any]] = None):
        self.knowledgeBaseId = knowledgeBaseId
        self.userId = userId
        self.bucketFileId = bucketFileId
        self.chunkIndex = chunkIndex
        self.content = content
        # Armazena como string JSON para compatibilidade com o banco
        if isinstance(embedding, np.ndarray):
            self.embedding = json.dumps(embedding.tolist())
        elif isinstance(embedding, list):
            self.embedding = json.dumps(embedding)
        elif isinstance(embedding, str):
            self.embedding = embedding
        else:
            raise ValueError("embedding deve ser np.ndarray, list ou str")
        self.meta = meta or {}

    @property
    def embedding_array(self) -> np.ndarray:
        """Retorna o embedding como um array numpy (vetor de 1536 dimensões)."""
        return np.array(json.loads(self.embedding))

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário conforme a interface DocumentEmbeddingInput."""
        return {
            "id": self.id,
            "knowledgeBaseId": self.knowledgeBaseId,
            "userId": self.userId,
            "bucketFileId": self.bucketFileId,
            "chunkIndex": self.chunkIndex,
            "content": self.content,
            "embedding": json.loads(self.embedding) if isinstance(self.embedding, str) else self.embedding,
            "meta": self.meta
        } 