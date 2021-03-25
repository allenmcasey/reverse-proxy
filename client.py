import socket
import hashlib
import json
import pickle
import sys


localhost = '127.0.0.1'
rp_port = int(sys.argv[2])
json_filename = sys.argv[3]

# create connection to reverse proxy
rp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rp_socket.connect((localhost, rp_port))

while True:

    # read/serialize message, then send/receive
    json_file = open(json_filename, "r")
    json_file_data = json.load(json_file)
    rp_socket.send(pickle.dumps(json_file_data))
    json_received_data = pickle.loads(rp_socket.recv(1024))

    # check if this is an error response
    if json_received_data["type"] == -1:
        print("Requested policy not found, please try again later...")
        break

    # get expected/received hashes
    expected_hash = str(hashlib.sha1(json_file_data['payload'].encode('ascii')).hexdigest())
    received_hash = json_received_data['payload']

    # test validity of hash
    if received_hash == expected_hash:
        print("Transmission successfully received by server")
        break
    else:
        user_answer = input("Transmission to server was corrupted. Do you want to try again? (y/n): ")
        if user_answer == 'y':
            continue
        else:
            break

rp_socket.close()
