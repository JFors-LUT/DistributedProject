from bs4 import BeautifulSoup
import pika
import json
import requests

class DataManager:
    def __init__(self):

        #create connection with pika 
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        #declares queue and consume. on receiving data on_request is called
        self.channel.queue_declare(queue='data_queue')
        self.channel.basic_consume(queue='data_queue', on_message_callback=self.on_request)

    def on_request(self, ch, method, props, body):
        #get data from received json
        message = json.loads(body.decode())
        url = message['url']
        website = message['content']
        corr_id = message['corr_id']

        #process data and return website body
        response = processData(url, website)

        #create response json to return to MicroManager 
        response = str(response)
        response_message = json.dumps({'content': response, 'corr_id': corr_id})

        ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=corr_id), body=response_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def processData(URL, returnSite):

    #turn website into BeautifulSoup object for processing
    soup = BeautifulSoup(returnSite, 'html.parser')

    #special case for iltalehti: get news titles, else return website body
    if URL == 'iltalehti.fi':
        dataPacket = caseIltalehti(soup)
        return dataPacket
    else:
        dataPacket = soup.find('body')
        return dataPacket
    
def caseIltalehti(soup):
    text = "" 

    for element in soup.find_all('div', class_='front-title a-title-font'):
        text += element.text.strip()+'\n'
    return text

if __name__ == '__main__':
    #initialize datamanager class and wait for incoming messages 
    manager = DataManager()

    print('Data Manager is running...')
    manager.channel.start_consuming()
    print('Data manager might not be running... ')
