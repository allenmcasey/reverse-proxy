# reverse-proxy

A small-scale implementation of a reverse proxy distributed system. 

In a typical reverse proxy system, there are two types of entities. First, we have the reverse proxy that keeps track of different devices that are connected and accessible through it. Second, the devices or nodes that connect to the reverse proxy. In our setup, there are two types of nodes -- client, which needs to send messages to a server, which is the second type of node. The reverse proxy and client/server are implemented in Python using basic socket interface. 

In this setup, we have a single reverse proxy and multiple clients and servers. The clients send text messages to a well-known port on the reverse proxy, which forwards the message to any server identified by a specific privacy policy, and the responding server sends to the client a SHA1 hash of the message. The client can then check if the server received the message correctly and display an appropriate transmission status message on the terminal. 

## Testing the project 


In the home directory of the repository, start the reverse proxy by typing ``python3 reverse_proxy.py 10000``.<br/><br/>

Next, type ``./start_servers.sh`` to start a set of servers identified by one of three different policies.<br/><br/>

To execute a couple dozen client requests that ask for permutations of all three available policies, type ``./test_clients.sh``. For each successful message from client -> reverse proxy -> server, you will see ``Transmission successfully received by server`` in the terminal.<br/><br/>

After you have finished testing the system, type ``./clean.sh`` to clean up the remaining server processes.



