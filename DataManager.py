from bs4 import BeautifulSoup
import pika
import json
import requests

class DataManager:
    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='data_queue')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='data_queue', on_message_callback=self.on_request)

    def on_request(self, ch, method, props, body):
        message = json.loads(body.decode())
        url = message['url']
        website = message['content']
        corr_id = message['corr_id']

        print(website, url, corr_id)

        #response = requests.get(url)
        response = processData(url, website)
        #if response == 0:
        #    response_message = ({'content': str(response), 'corr_id': corr_id})
        #else:
        response = str(response)
        response_message = json.dumps({'content': response, 'corr_id': corr_id})

        ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=corr_id), body=response_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def processData(URL, returnSite):

    soup = BeautifulSoup(returnSite, 'html.parser')

    if URL == 'iltalehti.fi':
        dataPacket = caseIltalehti(soup)
        return dataPacket
    else:
        dataPacket = soup.find('body')
        return dataPacket
    
def caseIltalehti(soup):
    text = "" 
    textList = []
    #titleClass = 

    for element in soup.find_all('div', class_='front-title a-title-font'):
        print(element.text.strip())
        text += element.text.strip()+'\n'
    return text

if __name__ == '__main__':
    manager = DataManager()

    print('Data Manager is running...')
    manager.channel.start_consuming()
