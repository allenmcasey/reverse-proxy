# reverse-proxy

Author: Allen Casey <br/>
Email:  allencasey337@gmail.com

This project small-scale implementation of a reverse proxy distributed system.

In a typical reverse proxy system, there are two types of entities. First, we have the reverse proxy that keeps track of different devices that are connected and accessible through it. Second, the devices or nodes that connect to the reverse proxy. In this setup, there are two types of nodes -- clients, which need to send messages to a server, which is the second type of node. The reverse proxy and client/server are implemented in Python using the basic socket interface. 

This system has a single reverse proxy and multiple clients and servers. The clients send JSON messages to a well-known port on the reverse proxy, which forwards the message to any server identified by a specific privacy policy, and the responding server sends to the client a SHA1 hash of the message. The client can then check if the server received the message correctly and display an appropriate transmission status message on the terminal. 

## Testing the project 

In the home directory of the repository, start the reverse proxy by typing ``python3 reverse_proxy.py 10000``.<br/><br/>

Next, start the server(s) by typing ``python3 server.py SERVER_ID POLICY PORT``, repling the all-caps arguments with integers of your choice. You can cahnge up the policy number to create servers of different policies, but all server ports you create must be unique.<br/><br/>

To execute a client request, type ``python3 client.py CLIENT_ID PROXY_PORT JSON_FILENAME``. There are 3 sample JSON packets included in the repository: client_packet_{1,2,3}.json. The number at the end of the filename indicates which policy the packet requests, and these packets can be used for simple tests of the system. For each successful message from client -> reverse proxy -> server, you will see ``Transmission successfully received by server`` in the terminal.<br/><br/>

## Fault Tolerance of the System

I decided to implement a fault-tolerance feature in the system that performs periodic health checks on the servers listed in the policy table. 


