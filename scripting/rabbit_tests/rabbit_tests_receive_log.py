import pika, sys, os
import time


def callback(ch, method, properties, body):
    print(f" [x] received {body}")
    # time.sleep(body.count(b'.'))
    print(" [x] Done")
    # ch.basic_ack(delivery_tag=method.delivery_tag)

# create the connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

# result = channel.queue_declare(queue='',
#                                exclusive=True)  # exclusive ensures the queue is deleted on connection close
private = channel.queue_declare(queue='private_queue',
                               exclusive=True)  # exclusive ensures the queue is deleted on connection close

print(' [*] Waiting for logs. To exit press CTRL+C')
# channel.queue_bind(exchange='logs',
#                    queue=result.method.queue)
channel.queue_bind(exchange='direct_logs',
                   queue=private.method.queue,
                   routing_key='private')

channel.basic_consume(queue=result.method.queue, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

