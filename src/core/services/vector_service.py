from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import numpy as np
import openai
import os
from src.models.document_embedding import DocumentEmbedding

class VectorService:
    def __init__(self, db: Session):
        self.db = db
        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise ValueError("OPENAI_KEY não encontrada nas variáveis de ambiente")
        openai.api_key = api_key

    def create_embedding(self, text: str) -> np.ndarray:
        """Gera um embedding para o texto fornecido usando a API da OpenAI."""
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-3-small"
            )
            return np.array(response["data"][0]["embedding"])
        except Exception as e:
            raise Exception(f"Erro ao gerar embedding com OpenAI: {str(e)}")

    def store_embedding(
        self,
        knowledgeBaseId: str,
        userId: str,
        bucketFileId: str,
        chunkIndex: int,
        content: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> DocumentEmbedding:
        """Armazena um novo embedding no banco de dados."""
        embedding = self.create_embedding(content)
        doc_embedding = DocumentEmbedding(
            knowledgeBaseId=knowledgeBaseId,
            userId=userId,
            bucketFileId=bucketFileId,
            chunkIndex=chunkIndex,
            content=content,
            embedding=embedding,
            meta=meta
        )
        self.db.add(doc_embedding)
        self.db.commit()
        self.db.refresh(doc_embedding)
        return doc_embedding

    def store_embeddings_batch(self, embeddings_data: list, batch_size: int = 2) -> List[DocumentEmbedding]:
        """
        Recebe uma lista de dicionários com os campos necessários e faz o insert em batch.
        Cada item deve conter: knowledgeBaseId, userId, bucketFileId, chunkIndex, content, meta (opcional).
        
        Args:
            embeddings_data: Lista de dicionários com os dados dos embeddings
            batch_size: Tamanho do lote para inserção (padrão: 2)
        """
        doc_embeddings = []
        total_items = len(embeddings_data)
        
        for i in range(0, total_items, batch_size):
            batch = embeddings_data[i:i + batch_size]
            batch_embeddings = []
            
            try:
                # Processa cada item do lote
                for data in batch:
                    embedding = self.create_embedding(data['content'])
                    doc_embedding = DocumentEmbedding(
                        knowledgeBaseId=data['knowledgeBaseId'],
                        userId=data['userId'],
                        bucketFileId=data['bucketFileId'],
                        chunkIndex=data['chunkIndex'],
                        content=data['content'],
                        embedding=embedding,
                        meta=data.get('meta')
                    )
                    batch_embeddings.append(doc_embedding)
                
                # Insere o lote no banco
                self.db.bulk_save_objects(batch_embeddings)
                self.db.commit()
                doc_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                # Em caso de erro, faz rollback e tenta novamente com um lote menor
                self.db.rollback()
                if batch_size > 1:
                    # Se o lote atual falhou e tem mais de 1 item, tenta inserir um por um
                    for item in batch:
                        try:
                            single_embedding = self.create_embedding(item['content'])
                            doc_embedding = DocumentEmbedding(
                                knowledgeBaseId=item['knowledgeBaseId'],
                                userId=item['userId'],
                                bucketFileId=item['bucketFileId'],
                                chunkIndex=item['chunkIndex'],
                                content=item['content'],
                                embedding=single_embedding,
                                meta=item.get('meta')
                            )
                            self.db.add(doc_embedding)
                            self.db.commit()
                            doc_embeddings.append(doc_embedding)
                        except Exception as single_error:
                            self.db.rollback()
                            raise Exception(f"Erro ao inserir embedding individual: {str(single_error)}")
                else:
                    # Se já está tentando inserir um por um e falhou, propaga o erro
                    raise Exception(f"Erro ao inserir lote de embeddings: {str(e)}")
        
        return doc_embeddings

    def search_similar(
        self,
        query: str,
        knowledge_base_id: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares à query fornecida.
        
        Args:
            query: Texto para buscar documentos similares
            knowledge_base_id: Opcional. Filtra por base de conhecimento
            limit: Número máximo de resultados
            threshold: Limiar de similaridade (0-1)
            
        Returns:
            Lista de documentos similares com suas distâncias
        """
        # Gera o embedding da query
        query_embedding = self.create_embedding(query)

        # Constrói a query SQL
        sql = """
            WITH query_embedding AS (
                SELECT :embedding::vector AS embedding
            )
            SELECT 
                de.*,
                1 - (de.embedding <=> query_embedding.embedding) as similarity
            FROM 
                document_embeddings de,
                query_embedding
            WHERE 
                1 - (de.embedding <=> query_embedding.embedding) > :threshold
        """
        params = {
            "embedding": query_embedding.tolist(),
            "threshold": threshold
        }

        if knowledge_base_id:
            sql += " AND de.knowledge_base_id = :knowledge_base_id"
            params["knowledge_base_id"] = knowledge_base_id

        sql += """
            ORDER BY similarity DESC
            LIMIT :limit
        """
        params["limit"] = limit

        # Executa a busca
        result = self.db.execute(text(sql), params)
        
        # Converte os resultados
        return [
            {
                "id": row.id,
                "knowledge_base_id": row.knowledge_base_id,
                "user_id": row.user_id,
                "bucket_file_id": row.bucket_file_id,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "meta": row.meta,
                "similarity": float(row.similarity),
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in result
        ]

    def get_by_knowledge_base(
        self,
        knowledge_base_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentEmbedding]:
        """Retorna todos os embeddings de uma base de conhecimento."""
        return (
            self.db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.knowledge_base_id == knowledge_base_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_by_knowledge_base(self, knowledge_base_id: str) -> int:
        """Remove todos os embeddings de uma base de conhecimento."""
        result = (
            self.db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.knowledge_base_id == knowledge_base_id)
            .delete()
        )
        self.db.commit()
        return result 