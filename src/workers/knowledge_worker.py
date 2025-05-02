import os
import json
import pika
import logging
from typing import Dict, Any, List
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeWorker:
    def __init__(self):
        # Configuração RabbitMQ
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
        self.queue_name = 'knowledge_base_processing'
        
        # Configuração MongoDB
        self.mongodb_uri = os.getenv('MONGODB_URI')
        self.mongodb_db = os.getenv('MONGODB_DB')
        
        # Configuração MinIO
        self.minio_endpoint = os.getenv('MINIO_ENDPOINT', 'minio.gwan.com.br')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'gwan')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'gwan123')
        self.minio_secure = os.getenv('MINIO_SECURE', 'true').lower() == 'true'
        
        # Log das configurações
        logger.info("=== Configurações do Worker ===")
        logger.info("RabbitMQ:")
        logger.info(f"  - Host: {self.rabbitmq_host}")
        logger.info(f"  - Port: {self.rabbitmq_port}")
        logger.info(f"  - User: {self.rabbitmq_user}")
        logger.info(f"  - Queue: {self.queue_name}")
        
        logger.info("\nMongoDB:")
        logger.info(f"  - URI: {self.mongodb_uri}")
        logger.info(f"  - Database: {self.mongodb_db}")
        
        logger.info("\nMinIO:")
        logger.info(f"  - Endpoint: {self.minio_endpoint}")
        logger.info(f"  - Access Key: {self.minio_access_key}")
        logger.info(f"  - Secure: {self.minio_secure}")
        logger.info("=============================\n")
        
        # Validação das variáveis de ambiente
        self._validate_env_vars()
        
        # Configuração das credenciais RabbitMQ
        self.credentials = pika.PlainCredentials(
            self.rabbitmq_user,
            self.rabbitmq_password
        )
        
        # Configuração dos parâmetros de conexão RabbitMQ
        self.parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            credentials=self.credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        # Inicializa conexão com MongoDB
        self.mongo_client = MongoClient(self.mongodb_uri)
        self.db = self.mongo_client[self.mongodb_db]

        # Inicializa cliente MinIO
        self.minio_client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=self.minio_secure
        )

    def _validate_env_vars(self):
        """Valida se todas as variáveis de ambiente necessárias estão definidas."""
        required_vars = {
            'RABBITMQ_HOST': self.rabbitmq_host,
            'RABBITMQ_USER': self.rabbitmq_user,
            'RABBITMQ_PASSWORD': self.rabbitmq_password,
            'MONGODB_URI': self.mongodb_uri,
            'MONGODB_DB': self.mongodb_db,
            'MINIO_ENDPOINT': self.minio_endpoint,
            'MINIO_ACCESS_KEY': self.minio_access_key,
            'MINIO_SECRET_KEY': self.minio_secret_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")

    def get_minio_file_info(self, bucket: str, object_name: str) -> Dict:
        """Busca informações do arquivo no MinIO."""
        try:
            logger.info("\n=== Tentando acessar arquivo no MinIO ===")
            logger.info(f"  - Bucket: {bucket}")
            logger.info(f"  - Object Name: {object_name}")
            
            # Verifica se o bucket existe
            bucket_exists = self.minio_client.bucket_exists(bucket)
            logger.info(f"  - Bucket existe? {bucket_exists}")
            
            if not bucket_exists:
                logger.error(f"Bucket não encontrado: {bucket}")
                return None

            # Busca informações do objeto
            stat = self.minio_client.stat_object(bucket, object_name)
            logger.info("  - Objeto encontrado com sucesso!")
            
            return {
                'size': stat.size,
                'last_modified': stat.last_modified.isoformat(),
                'etag': stat.etag,
                'content_type': stat.content_type
            }
        except S3Error as e:
            logger.error(f"Erro S3 ao buscar informações do arquivo no MinIO: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao acessar MinIO: {str(e)}")
            logger.error(f"Tipo do erro: {type(e)}")
            return None
        finally:
            logger.info("===============================\n")

    def get_user_data(self, user_id: str) -> Dict:
        """Busca dados do usuário no MongoDB."""
        try:
            user = self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                # Converte ObjectId para string para serialização JSON
                user['_id'] = str(user['_id'])
                if user.get('lastLoginAt'):
                    user['lastLoginAt'] = user['lastLoginAt'].isoformat()
                if user.get('loginCodeExpiresAt'):
                    user['loginCodeExpiresAt'] = user['loginCodeExpiresAt'].isoformat()
                return user
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar dados do usuário: {e}")
            return None

    def get_knowledge_base_data(self, knowledge_base_id: str) -> Dict:
        """Busca dados da knowledge base no MongoDB."""
        try:
            kb = self.db.knowledgebases.find_one({"_id": ObjectId(knowledge_base_id)})
            if kb:
                # Converte ObjectId para string para serialização JSON
                kb['_id'] = str(kb['_id'])
                if kb.get('createdAt'):
                    kb['createdAt'] = kb['createdAt'].isoformat()
                if kb.get('updatedAt'):
                    kb['updatedAt'] = kb['updatedAt'].isoformat()
                return kb
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar dados da knowledge base: {e}")
            return None

    def get_bucket_file_data(self, file_id: str) -> Dict:
        """Busca dados do arquivo no MongoDB."""
        try:
            file = self.db.bucketfiles.find_one({"_id": ObjectId(file_id)})
            if file:
                # Converte ObjectId para string para serialização JSON
                file['_id'] = str(file['_id'])
                if file.get('createdAt'):
                    file['createdAt'] = file['createdAt'].isoformat()
                if file.get('updatedAt'):
                    file['updatedAt'] = file['updatedAt'].isoformat()
                return file
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar dados do arquivo: {e}")
            return None

    def list_bucket_files(self, bucket_name: str) -> List[Dict]:
        """Lista todos os arquivos em um bucket."""
        try:
            logger.info(f"\n=== Listando arquivos do bucket: {bucket_name} ===")
            objects = self.minio_client.list_objects(bucket_name)
            files = []
            
            for obj in objects:
                file_info = {
                    'object_name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified.isoformat()
                }
                files.append(file_info)
                logger.info(f"Arquivo encontrado: {json.dumps(file_info, indent=2)}")
            
            logger.info(f"Total de arquivos encontrados: {len(files)}")
            return files
        except S3Error as e:
            logger.error(f"Erro ao listar arquivos do bucket: {str(e)}")
            return []

    def download_file(self, bucket_name: str, object_name: str, local_path: str) -> bool:
        """Baixa um arquivo do MinIO."""
        try:
            logger.info(f"\n=== Baixando arquivo do MinIO ===")
            logger.info(f"Bucket: {bucket_name}")
            logger.info(f"Arquivo: {object_name}")
            logger.info(f"Destino: {local_path}")

            # Cria o diretório de destino se não existir
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Baixa o arquivo
            self.minio_client.fget_object(
                bucket_name,
                object_name,
                local_path
            )
            
            logger.info("Arquivo baixado com sucesso!")
            return True
        except S3Error as e:
            logger.error(f"Erro ao baixar arquivo: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar arquivo: {str(e)}")
            return False

    def process_message(self, ch, method, properties, body):
        """Processa a mensagem recebida da fila."""
        try:
            # Decodifica a mensagem
            message = json.loads(body.decode())
            logger.info("\n=== Nova Mensagem Recebida ===")
            logger.info(f"Conteúdo da mensagem: {json.dumps(message, indent=2)}")
            
            # Extrai os parâmetros
            knowledge_base_id = message.get('knowledgeBaseId')
            file_id = message.get('fileId')
            user_id = message.get('userId')
            filename = message.get('filename')
            
            logger.info("\nParâmetros extraídos:")
            logger.info(f"  - Knowledge Base ID: {knowledge_base_id}")
            logger.info(f"  - File ID: {file_id}")
            logger.info(f"  - User ID: {user_id}")
            logger.info(f"  - Filename: {filename}")
            
            # Busca dados do usuário
            user_data = self.get_user_data(user_id)
            if user_data:
                logger.info("Dados do usuário encontrados:")
                logger.info(f"  - Nome: {user_data.get('name')}")
                logger.info(f"  - Email: {user_data.get('email')}")
                logger.info(f"  - WhatsApp: {user_data.get('whatsapp')}")
                logger.info(f"  - Status: {'Ativo' if user_data.get('isActive') else 'Inativo'}")
                logger.info(f"=============================================")
            else:
                logger.warning(f"Usuário não encontrado: {user_id}")

            # Busca dados da knowledge base
            kb_data = self.get_knowledge_base_data(knowledge_base_id)
            if kb_data:
                logger.info("Dados da Knowledge Base encontrados:")
                logger.info(f"  - Nome: {kb_data.get('name')}")
                logger.info(f"  - Descrição: {kb_data.get('description')}")
                logger.info(f"  - Status: {kb_data.get('status')}")
                logger.info(f"  - Criado em: {kb_data.get('createdAt')}")
                logger.info(f"=============================================")
            else:
                logger.warning(f"Knowledge Base não encontrada: {knowledge_base_id}")

            # Busca dados do arquivo
            file_data = self.get_bucket_file_data(file_id)
            if file_data:
                logger.info("Dados do arquivo encontrados:")
                logger.info(f"  - Nome do arquivo: {file_data.get('filename')}")
                logger.info(f"  - Tipo: {file_data.get('mimetype')}")
                logger.info(f"  - Tamanho: {file_data.get('size')} bytes")
                logger.info(f"  - Bucket: {file_data.get('bucket')}")
                logger.info(f"  - Status: {file_data.get('status')}")
                logger.info(f"=============================================")

                # Lista arquivos no bucket
                bucket_name = file_data.get('bucket', 'datasets')
                bucket_files = self.list_bucket_files(bucket_name)
                
                # Define o caminho local para download
                downloads_dir = os.path.join(os.getcwd(), 'downloads')
                local_file_path = os.path.join(downloads_dir, filename)

                # Baixa o arquivo
                if self.download_file(bucket_name, filename, local_file_path):
                    logger.info(f"Arquivo baixado com sucesso para: {local_file_path}")
                    
                    # Aqui você pode adicionar o processamento do arquivo
                    # Por exemplo, extrair texto, processar com ML, etc.
                    
                else:
                    logger.error("Falha ao baixar arquivo")
                    # Atualiza o status da knowledge base para 'failed'
                    self.update_knowledge_base_status(knowledge_base_id, 'failed', 'Falha ao baixar arquivo')
            else:
                logger.warning(f"Arquivo não encontrado: {file_id}")
            
            # Confirma o processamento da mensagem
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar mensagem: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def update_knowledge_base_status(self, knowledge_base_id: str, status: str, error: str = None):
        """Atualiza o status da knowledge base."""
        try:
            update_data = {'status': status}
            if error:
                update_data['error'] = error

            self.db.knowledgebases.update_one(
                {'_id': ObjectId(knowledge_base_id)},
                {'$set': update_data}
            )
            logger.info(f"Status da knowledge base atualizado: {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status da knowledge base: {str(e)}")

    def start(self):
        """Inicia o worker e começa a consumir mensagens."""
        try:
            # Estabelece conexão com o RabbitMQ
            connection = pika.BlockingConnection(self.parameters)
            channel = connection.channel()
            
            # Declara a fila
            channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Configura o QoS
            channel.basic_qos(prefetch_count=1)
            
            # Configura o consumidor
            channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.process_message
            )
            
            logger.info(f"Iniciando worker para a fila: {self.queue_name}")
            logger.info("Aguardando mensagens...")
            
            # Inicia o consumo de mensagens
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Erro de conexão com RabbitMQ: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
        finally:
            if 'connection' in locals() and connection.is_open:
                connection.close()
            if hasattr(self, 'mongo_client'):
                self.mongo_client.close()

if __name__ == "__main__":
    worker = KnowledgeWorker()
    worker.start() 