import socket
import hashlib
import json
import pickle
import sys

rp_domain = sys.argv[1]
rp_port = int(sys.argv[2])
json_filename = sys.argv[3]

while True:

    # read message
    json_file = open(json_filename, "r")
    json_file_data = json.load(json_file)

    # check payload size
    if len(json_file_data['payload']) > 1024:
        print("Packet payload is too large, please send a message smaller than 1024 bytes.")
        break

    # create connection to reverse proxy
    rp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rp_socket.connect((rp_domain, rp_port))

    # serialize message, then send/receive
    rp_socket.send(pickle.dumps(json_file_data))
    json_received_data = pickle.loads(rp_socket.recv(1024))

    # check if this is an error response
    if json_received_data["type"] == -1:
        print("Requested policy not found, please try again later...")
        rp_socket.close()
        break

    # get expected/received hashes
    expected_hash = str(hashlib.sha1(json_file_data['payload'].encode('ascii')).hexdigest())
    received_hash = json_received_data['payload']

    # test validity of hash
    if received_hash == expected_hash:
        print("Transmission successfully received by server")
        rp_socket.close()
        break
    else:
        user_answer = input("Transmission to server was corrupted. Do you want to try again? (y/n): ")
        rp_socket.close()
        if user_answer == 'y':
            continue
        else:
            break

