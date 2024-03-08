import pika, sys, os


def main():
    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # create a queue for messages
    channel.queue_declare(queue='durable_queue', durable=True)
    channel.basic_qos(
        prefetch_count=2)  # ensures workers are assigned 2 tasks at a time (you can also use 1), also TTL to set
    print(f" Creating message")
    # create message
    message = ' '.join(sys.argv[1:]) or "Hello World!"

    # send a message
    channel.basic_publish(exchange='logs',
                          routing_key='durable_queue',
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE  # ensures message survives restart
                          ))

    print(f" [x] Sent {message}")
    # close the connection
    # connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
