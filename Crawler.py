import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pika


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def runCrawler():
    channel.queue_declare(queue='fetcher_queue')
    channel.exchange_declare(exchange='fetcher_exchange', exchange_type='direct')
    channel.queue_bind(queue='fetcher_queue', exchange='fetcher_exchange', routing_key='fetcher_key')
    channel.basic_consume(queue='fetcher_queue', on_message_callback=callback, auto_ack=True)
    print("Crawler is waiting for messages...")
    while True:
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print('Interrupted')
        break

    # close connection
    connection.close()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    response = getContent(body.decode())
    soup = BeautifulSoup(response.text, 'html.parser')
    page_title = soup.title.string
    print(f" [x] Page title: {page_title}")
    channel.queue_declare(queue='result_queue')
    channel.basic_publish(exchange='', routing_key='result_queue', body=page_title.encode())



def getContent(message):
    try:
        session = requests.Session()
        retry = Retry(connect=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if message[:4] == "http":
            response = requests.get(message)
            #soup = BeautifulSoup(response.content, 'html.parser')
            return response

        else:
            message = 'https://'+message
            response = session.get(message)
            #soup = BeautifulSoup(response.content, 'html.parser')
            #body_text = soup.find('body')
            return response
            #return response
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        print("failed")
        return 0

if __name__ == '__main__':
    runCrawler()
