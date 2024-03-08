import pika
import sys
import os
import time


def callback(ch, method, properties, body):
    print(f" [x] received {method.routing_key}:{body}")
    # time.sleep(body.count(b'.'))
    print(" [x] Done")
    # ch.basic_ack(delivery_tag=method.delivery_tag)


# create the connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
# channel.exchange_declare(exchange='logs',
#                          exchange_type='fanout')
channel.exchange_declare(exchange='topic_logs',
                         exchange_type='topic')

# result = channel.queue_declare(queue='',
#                                exclusive=True)  # exclusive ensures the queue is deleted on connection close
topic = channel.queue_declare(queue='',
                                exclusive=True)  # exclusive ensures the queue is deleted on connection close

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(
        exchange='topic_logs', queue=topic.method.queue, routing_key=binding_key)
print(f' [*] Waiting for logs with keys: {binding_keys}. To exit press CTRL+C')
# channel.queue_bind(exchange='logs',
#                    queue=result.method.queue)

channel.basic_consume(queue=topic.method.queue, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
