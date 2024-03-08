import pika, sys, os


def main():
    # create the connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='topic_logs',
                             exchange_type='topic')
    # channel.exchange_declare(exchange='logs',
    #                          exchange_type='fanout')

    severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
    # message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
    message = ''.join(sys.argv[2:]) or 'hahahaha, noob'

    channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)
    print(f" [x] Sent {severity}:{message}")
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
