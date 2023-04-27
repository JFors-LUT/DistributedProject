import pika
import json
import requests
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='crawler_queue')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='crawler_queue', on_message_callback=self.on_request)

    def on_request(self, ch, method, props, body):
        message = json.loads(body.decode())
        url = message['url']
        corr_id = message['corr_id']

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string

        response_message = json.dumps({'title': title, 'corr_id': corr_id})

        ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=corr_id), body=response_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    crawler = Crawler()

    print('Crawler is running...')
    crawler.channel.start_consuming()
