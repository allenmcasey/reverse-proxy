import socket
import hashlib
from _thread import *
import pickle
import sys

# TODO (maybe) exit keyword for servers
# servers listen for a keyword (e.g., 'exit') and terminate
# when it is inputted by the user


def handle_connection(client):

    # data received from client
    json_data = pickle.loads(client.recv(1024))
    print("message received from client via proxy. client id:", json_data["srcid"])

    # update payload with its SHA1 hash and return to client
    json_data["payload"] = str(hashlib.sha1(json_data["payload"].encode("ascii")).hexdigest())
    json_data["type"] = 2
    client.send(pickle.dumps(json_data))
    client.close()


def Main():

    localhost = "127.0.0.1"
    reverse_policy_port = 10000
    this_id = int(sys.argv[1])
    this_policy = int(sys.argv[2])
    this_port = int(sys.argv[3])

    # create socket to listen on
    in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_socket.bind((localhost, this_port))
    in_socket.listen(6)
    print("server socket listening... bound to port", this_port)

    # create socket with reverse proxy
    rp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rp.connect((localhost, reverse_policy_port))

    # create a setup packet
    setup_json_data = {
        "type": 1,
        "id": this_id,
        "privPoliId": this_policy,
        "listenport": this_port
    }

    # send setup packet to RP
    rp.send(pickle.dumps(setup_json_data))
    rp.close()

    while True:

        # accept a new connection
        c, address = in_socket.accept()
        print("Connected to:", address[0], "on port", address[1])
        start_new_thread(handle_connection, (c,))


if __name__ == '__main__':
    Main() 