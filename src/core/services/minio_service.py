from minio import Minio

class MinioService:
    def __init__(self, endpoint, access_key, secret_key, secure):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    # Adicione métodos conforme necessário 