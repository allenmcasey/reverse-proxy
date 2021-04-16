import socket
import hashlib
from _thread import *
import pickle
import sys


def handle_connection(client):

    # data received from client
    json_data = pickle.loads(client.recv(1024))

    # if client request
    if json_data["type"] == 0:

        # update payload with its SHA1 hash and return to client
        print("message received from client via proxy. client id:", json_data["srcid"])
        json_data["payload"] = str(hashlib.sha1(json_data["payload"].encode("ascii")).hexdigest())
        json_data["type"] = 2
        client.send(pickle.dumps(json_data))

    client.close()


def Main():

    reverse_proxy_port = 10000
    this_id = 2
    this_policy = 2
    this_port = 10001

    # create socket to listen on
    in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_socket.bind(("", this_port))
    in_socket.listen(6)
    print("server socket listening... bound to port", this_port)

    # create socket with reverse proxy
    reverse_proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reverse_proxy_socket.connect(("3.20.189.253", reverse_proxy_port))

    # create a setup packet
    setup_json_data = {
        "type": 1,
        "id": this_id,
        "privPoliId": this_policy,
        "listenport": this_port
    }

    # send setup packet to RP
    reverse_proxy_socket.send(pickle.dumps(setup_json_data))
    reverse_proxy_socket.close()

    while True:

        # accept a new connection
        connection, address = in_socket.accept()
        start_new_thread(handle_connection, (connection,))


if __name__ == '__main__':
    Main() 
