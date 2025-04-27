import json
import pika
import os
from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.core.pdf_processor import PDFProcessor
from src.models.pdf_processing import PDFProcessing

class PDFWorker:
    def __init__(self):
        # Configuração do RabbitMQ
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
        
        # Nome da fila
        self.queue_name = "pdf_processing"
        
        # Inicializa a conexão
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Estabelece conexão com o RabbitMQ."""
        try:
            # Cria as credenciais
            credentials = pika.PlainCredentials(
                self.rabbitmq_user,
                self.rabbitmq_password
            )
            
            # Cria os parâmetros de conexão
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials
            )
            
            # Estabelece a conexão
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declara a fila
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Configura o QoS
            self.channel.basic_qos(prefetch_count=1)
        except Exception as e:
            raise Exception(f"Erro ao conectar ao RabbitMQ: {str(e)}")

    def process_message(self, ch, method, properties, body):
        """Processa uma mensagem da fila."""
        try:
            # Decodifica a mensagem
            message = json.loads(body)
            
            # Obtém uma sessão do banco de dados
            db = SessionLocal()
            
            try:
                # Processa o PDF
                processor = PDFProcessor(db)
                result = processor.process_pdf(
                    file_data=message["file_data"],
                    prompt=message["prompt"],
                    filename=message["filename"],
                    user_id=message["user_id"]
                )
                
                # Confirma o processamento da mensagem
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                # Em caso de erro, atualiza o status no banco
                processing = db.query(PDFProcessing).filter(
                    PDFProcessing.id == message["processing_id"]
                ).first()
                if processing:
                    processing.status = "failed"
                    processing.error_message = str(e)
                    db.commit()
                
                # Rejeita a mensagem e a recoloca na fila
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            finally:
                db.close()
        except Exception as e:
            print(f"Erro ao processar mensagem: {str(e)}")
            # Rejeita a mensagem e a recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Inicia o worker."""
        try:
            # Configura o consumidor
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.process_message
            )
            
            print("Worker iniciado. Aguardando mensagens...")
            self.channel.start_consuming()
        except Exception as e:
            print(f"Erro ao iniciar worker: {str(e)}")
        finally:
            self.close()

    def close(self):
        """Fecha a conexão com o RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

if __name__ == "__main__":
    worker = PDFWorker()
    worker.start() 