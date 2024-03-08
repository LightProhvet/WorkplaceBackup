import pika, sys, os


def main():
    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='logs',
                             exchange_type='fanout')

    message = ' '.join(sys.argv[1:]) or "info: Hello World!"

    channel.basic_publish(exchange='logs', routing_key="", body=message)
    print(f" [x] sent {message}")
    connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
