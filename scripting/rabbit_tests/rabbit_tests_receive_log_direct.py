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
channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

# result = channel.queue_declare(queue='',
#                                exclusive=True)  # exclusive ensures the queue is deleted on connection close
private = channel.queue_declare(queue='',
                                exclusive=True)  # exclusive ensures the queue is deleted on connection close

severities = sys.argv[1:]
if not severities:
    sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)

for severity in severities:
    channel.queue_bind(
        exchange='direct_logs', queue=private.method.queue, routing_key=severity)
print(f' [*] Waiting for logs with severities {severities}. To exit press CTRL+C')
# channel.queue_bind(exchange='logs',
#                    queue=result.method.queue)

channel.basic_consume(queue=private.method.queue, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
