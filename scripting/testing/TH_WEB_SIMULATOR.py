import pika
import sys
import datetime

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
                         exchange_type='topic')

queue_keys = ['modified_queue', 'created_queue', 'deleted_queue', 'data_queue']
for queue in queue_keys:
    channel.queue_declare(queue=queue)

binding_keys = ['*.modified.*', '*.created.*', '*.deleted.*', '*.*.data']
i = 0
for binding_key in binding_keys:
    channel.queue_bind(
        exchange='topic_logs', queue=queue_keys[i], routing_key=binding_key)
    i += 1


def callback_on_request(ch, method, props, body):
    print(f"\n\nReceived topic: {method.routing_key} at {datetime.datetime.now()} with BODY: \n {body})")
    response = "GOOD"
    if props.reply_to:
        route_key = props.reply_to
    else:
        route_key = ""
    ch.basic_publish(
        exchange='',
        routing_key=route_key,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [queue_name]...\n" % sys.argv[0])
    sys.exit(1)
binding_key = binding_keys[0]



channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=binding_key, on_message_callback=callback_on_request)
print(f' Waiting for logs for queue: {binding_key}. To exit press CTRL+C')
channel.start_consuming()
