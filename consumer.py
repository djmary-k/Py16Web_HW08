import json
import os
import sys
import time
import pika
from mongoengine import connect, Document, StringField, BooleanField

connect(db='web16', host="mongodb://localhost:27017")


class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(required=False)


def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='web_16_queue', durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        print(f" [x] Received {message}")
        time.sleep(0.5)

        contact_id = message['id']
        contact = Contact.objects(id=contact_id).first()
        if contact:
            contact.message_sent = True
            contact.save()
        print(f" [x] Completed {method.delivery_tag} task")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='web_16_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
