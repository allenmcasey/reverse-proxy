import socket
from _thread import *
import pickle
import sys

# TODO server validity check:
# when RP sends to server, if server doesn't accept request,
# remove from policy table, and rotate through all servers
# with that policy until one does if none work, return error

server_policies = {}        # dict to group servers by policy
policy_index = {}           # dict to map policy to round robin index
localhost = '127.0.0.1'
this_port = int(sys.argv[1])


def get_server_port(policy):

    # round-robin functionality
    if policy_index[policy] < len(server_policies[policy]):
        port = server_policies[policy][policy_index[policy]][1]
    else:
        policy_index[policy] = 0
        port = server_policies[policy][policy_index[policy]][1]
    policy_index[policy] += 1

    return port


def handle_request(client):

    # unpack data received from client
    json_data = pickle.loads(client.recv(1024))
    policy = json_data['privPoliId']

    # if client request packet
    if json_data['type'] == 0:

        # create connection
        print("client request packet received. client id:", json_data['srcid'])
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_port_num = get_server_port(policy)
        server_socket.connect((localhost, server_port_num))

        # forward request to appropriate server
        server_socket.send(pickle.dumps(json_data))
        print("client request packet forwarded")

        # forward server response to client
        client.send(server_socket.recv(1024))
        print("server response received and forwarded back to client")
        server_socket.close()
        client.close()

    # if server setup packet
    elif json_data['type'] == 1:

        # update policy table(s)
        print("server setup packet received. server id:", json_data['id'])
        new_entry = [json_data["id"], json_data["listenport"]]
        if policy in server_policies:
            server_policies[policy].append(new_entry)
        else:
            server_policies[policy] = [new_entry]
            policy_index[policy] = 0

        print("server policy table:", server_policies)
        print("policy index table:", policy_index)


def Main():

    # create inbound socket to listen on
    in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_socket.bind((localhost, this_port))
    in_socket.listen(6)
    print("rp socket listening... bound to port", this_port)

    while True:

        # accept new connection
        c, address = in_socket.accept()
        print('Connected to:', address[0], 'on port', address[1])
        start_new_thread(handle_request, (c,))


if __name__ == '__main__':
    Main()
