import pika
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):

         #create connection with pika 
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        #declares queue and consume. on receiving data on_request is called
        self.channel.queue_declare(queue='crawler_queue')
        self.channel.basic_consume(queue='crawler_queue', on_message_callback=self.on_request)


    def on_request(self, ch, method, props, body):
        #json for api
        message = json.loads(body.decode())
        url = message['url']
        corr_id = message['corr_id']
        #fetch website 
        response = getContent(url)

        #proces response with BeautifulSoup object and turn to string for JSON return
        if response != 0:
            soup = BeautifulSoup(response.content, 'html.parser')
            response = str(soup)
            #title = soup.title.string
        response_message = json.dumps({'content': response, 'corr_id': corr_id})

        ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=corr_id), body=response_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def getContent(message):
    try:
        session = requests.Session()
        retry = Retry(connect=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if message[:4] == "http":
            response = requests.get(message)
            return response
        else:
            message = 'https://'+message
            response = session.get(message)

            return response

    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        return 0        

if __name__ == '__main__':
    crawler = Crawler()

    print('Crawler is running...')
    crawler.channel.start_consuming()
