import socket
from _thread import *
import threading
import pickle
import sys
import time


server_policies = {}        # dict to group servers by policy
policy_index = {}           # dict to map policy to round robin index
lock = threading.Lock()
localhost = '127.0.0.1'
this_port = int(sys.argv[1])


# given a policy, find a server
def get_server_port(policy):

    if policy not in server_policies or len(server_policies[policy]) == 0:
        print("Could not find server with requested policy... aborting")
        return -1

    # round-robin functionality
    if policy_index[policy] < len(server_policies[policy]):
        port = server_policies[policy][policy_index[policy]][1]
    else:
        policy_index[policy] = 0
        port = server_policies[policy][policy_index[policy]][1]
    with lock:
        policy_index[policy] += 1

    return port


# forward client request to server, and relay server response
def handle_client_request(client, json_data, policy):

    # initialize server socket; attempt to get a server port number
    print("client request packet received. client id:", json_data['srcid'])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_port_num = get_server_port(policy)

    # requested policy not found; abort
    if server_port_num == -1:
        json_data["type"] = -1
        client.send(pickle.dumps(json_data))

    else:

        # forward client's request to appropriate server
        server_socket.connect((localhost, server_port_num))
        server_socket.send(pickle.dumps(json_data))
        print("client request packet forwarded")

        # forward server's response to client
        client.send(server_socket.recv(1024))
        print("server response received and forwarded back to client")

    server_socket.close()
    client.close()


# add new server to policy table
def set_up_server(json_data, policy):

    # update policy table(s)
    print("server setup packet received. server id:", json_data['id'])
    new_entry = [json_data["id"], json_data["listenport"]]
    if policy in server_policies:
        with lock:
            server_policies[policy].append(new_entry)
    else:
        with lock:
            server_policies[policy] = [new_entry]
        policy_index[policy] = 0

    print("server policy table:", server_policies)
    print("policy index table:", policy_index)


# process an incoming connection
def handle_incoming_request(client):

    # unpack data received from request
    json_data = pickle.loads(client.recv(1024))
    policy = json_data['privPoliId']

    # if client request packet
    if json_data['type'] == 0:
        handle_client_request(client, json_data, policy)

    # if server setup packet
    elif json_data['type'] == 1:
        set_up_server(json_data, policy)


# given a server, determine if it's still alive
def test_server(policy, index, probe_message):

    # test connection with this server
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = test_socket.connect_ex((localhost, server_policies[policy][index][1]))

    # remove if dead
    if result != 0:
        del server_policies[policy][index]
        server_is_dead = True
    else:
        test_socket.send(probe_message)
        server_is_dead = False
    test_socket.close()
    return server_is_dead


# check health of all entries in policy table
def verify_servers_in_table(delay):

    # create probing packet
    probe_message = pickle.dumps({"type": -2})

    while True:

        # check that servers are still alive
        for key in server_policies.keys():
            for index in range(len(server_policies[key])):
                server_is_dead = test_server(key, index, probe_message)
                if server_is_dead:
                    break

        # wait 'delay' sec(s)
        time.sleep(delay)


def Main():

    test_delay = 1
    start_new_thread(verify_servers_in_table, (test_delay,))

    # create well-known inbound socket to listen on
    in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_socket.bind((localhost, this_port))
    in_socket.listen(6)
    print("rp socket listening... bound to port", this_port)

    while True:

        # accept new connection
        c, address = in_socket.accept()
        print('Connected to:', address[0], 'on port', address[1])
        start_new_thread(handle_incoming_request, (c,))


if __name__ == '__main__':
    Main()
