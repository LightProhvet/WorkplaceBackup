import pika, sys, os

def main():
    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # create a queue for messages
    channel.queue_declare(queue='hello')

    # send a message
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body='Hello World!')
    # close the connection
    connection.close()
