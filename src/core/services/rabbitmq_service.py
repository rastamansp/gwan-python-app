import pika

class RabbitMQService:
    def __init__(self, host, port, user, password, queue):
        self.credentials = pika.PlainCredentials(user, password)
        self.parameters = pika.ConnectionParameters(
            host=host, port=port, credentials=self.credentials,
            heartbeat=600, blocked_connection_timeout=300
        )
        self.queue = queue

    def consume(self, callback):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue, on_message_callback=callback)
        channel.start_consuming() 