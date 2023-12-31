import json
from datetime import datetime
import pika
from mongoengine import connect, Document, StringField, BooleanField

connect(db='web16', host="mongodb://localhost:27017")

class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(required=False)


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='Web16 exchange', exchange_type='direct')
channel.queue_declare(queue='web_16_queue', durable=True)
channel.queue_bind(exchange='Web16 exchange', queue='web_16_queue')


def create_tasks(nums: int):
    for i in range(nums):
        contact = Contact(fullname=f"Name {i}", email=f"user{i}@example.com")
        contact.save()

        message = {
            'id': str(contact.id),
            'payload': f"Date: {datetime.now().isoformat()}"
        }

        channel.basic_publish(exchange='Web16 exchange', routing_key='web_16_queue', body=json.dumps(message).encode())

    connection.close()


if __name__ == '__main__':
    create_tasks(100)
