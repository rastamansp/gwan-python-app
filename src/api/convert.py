from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from minio import Minio
import os
import pika
import json
from datetime import datetime
import uuid

router = APIRouter(prefix="/convert", tags=["convert"])

# Configuração do MinIO
minio_client = Minio(
    "minio.gwan.com.br",
    access_key="admin",
    secret_key="pazdeDeus@2025",
    secure=True
)

# Configuração do RabbitMQ
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "root"),
        os.getenv("RABBITMQ_PASSWORD", "pazdeDeus2025")
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq.gwan.com.br"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=credentials,
        ssl=True
    )
    return pika.BlockingConnection(parameters)

@router.post("/")
async def convert_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    prompt: str = Form(...)
):
    try:
        # Gera um ID único para o arquivo
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{file_id}{file_extension}"
        
        # Lê o conteúdo do arquivo
        file_content = await file.read()
        
        # Upload para o MinIO
        minio_client.put_object(
            bucket_name="pdfs",
            object_name=file_name,
            data=file_content,
            length=len(file_content),
            content_type=file.content_type
        )
        
        # Prepara a mensagem para o RabbitMQ
        message = {
            "file_id": file_id,
            "file_name": file_name,
            "user_id": user_id,
            "prompt": prompt,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Envia para o RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declara a fila
        channel.queue_declare(queue="pdf_conversion", durable=True)
        
        # Publica a mensagem
        channel.basic_publish(
            exchange="",
            routing_key="pdf_conversion",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # torna a mensagem persistente
            )
        )
        
        connection.close()
        
        return {
            "message": "Arquivo recebido e enviado para processamento",
            "file_id": file_id,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 