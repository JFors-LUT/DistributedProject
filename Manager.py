import pika
import json
import uuid

class MicroManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = self.result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()

    def send_request(self, url):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        message = json.dumps({'url': url, 'corr_id': self.corr_id})

        self.channel.basic_publish(exchange='', routing_key='crawler_queue', properties=pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id,), body=message)

        while self.response is None:
            self.connection.process_data_events()

        return self.response

if __name__ == '__main__':
    micro_manager = MicroManager()

    # Send a URL to Crawler
    while True:
        input("")
        url = 'https://www.google.com'
        response = micro_manager.send_request(url)

        print(response)