# reverse-proxy

Author: Allen Casey <br/>
Email:  allencasey337@gmail.com

This project is a small-scale implementation of a reverse proxy distributed system, implemented using the Python socket interface.

In a typical reverse proxy system, there are three components: clients, servers, and the reverse proxy application itself. This system contains one reverse proxy and multiple clients and servers. The clients and servers both connect to the reverse proxy, which acts like a middleman between the two other groups of applications. The clients send JSON requests to a well-known port on the reverse proxy, which forwards the message to an appropriate server identified by a privacy policy indicated in the client request packet. Here, the reverse proxy utilizes a round robin scheme to facilitate load-balancing among servers of each policy group. The responding server sends a SHA1 hash of the client's message back to the reverse proxy, which the reverse proxy then forwards back to the client. The client can then check if the server received the message correctly and display an appropriate transmission status message on the terminal.

## Testing the Project 

In the home directory of the repository, start the reverse proxy by typing ``python3 reverse_proxy.py 10000``.<br/><br/>

Next, start the server(s) by typing ``python3 server.py SERVER_ID POLICY PORT``, repling the all-caps arguments with integers of your choice. You can cahnge up the policy number to create servers of different policies, but all server ports you create must be unique.<br/><br/>

To execute a client request, type ``python3 client.py CLIENT_ID PROXY_PORT JSON_FILENAME``. There are 3 sample JSON packets included in the repository: client_packet_{1,2,3}.json. The number at the end of the filename indicates which policy the packet requests, and these packets can be used for simple tests of the system. For each successful message from client -> reverse proxy -> server, you will see ``Transmission successfully received by server`` in the terminal.<br/><br/>

## Fault Tolerance of the System

I implemented a fault-tolerance feature in the system that performs periodic health checks on the servers listed in the policy table. This way, the reverse proxy program can actively detect when servers fail, and update the policy table accordingly. To implement this, I created a separate threaded method running at all times in the reverse proxy program. Once each second, this method loops through the entire policy table and makes test connections with each server. When a connection is refused, the server listing is removed from the policy table, and the round robin index for that policy is reset to 0 to avoid any out-of-bounds errors.<br/><br/>

## Description of the Client, Server, and Reverse Proxy

The client file is the simplest of the three components. It opens a socket connection with the port specified in the args, and serializes a JSON object from the file specified in the args. It then sends the message to the reverse proxy and waits for a response. When the response is received - and if the response is not an error message - the client compares the received SHA1 hash payload with the SHA1 hash of the payload that was sent. If they're equal, we know that the server received the correct message, and we can terminate the program. If there is a discrepancy, we ask the user if they want to try again. 

The server begins by creating a port to listen on, then it establishes a connection with the reverse proxy. It sends the reverse proxy a setup packet of type 1 in order to be added to the policy table, then waits for forwarded messages from clients. When a client message is received, The server generates the SHA1 hash of the packet's payload, and sends the response message containing the hash back along the same connection. This response functionality is done inside a threaded function, so the server can handle multiple requests concurrently.

The reverse proxy first defines two dictionary structures: one that maps policy numbers to a list of <server_id, server_port> tuples, and one that maps policy numbers to the current index of that policy's round robin pointer. The pointer indicates an index in the list in the first dictionary associated with the policy, and each time a server is sent a message, the pointer is either incremented or reset to zero if it points to the last server in the list. Next, the program begins the threaded server-health-check function described in the Fault Tolerance section above. The reverse proxy then establishes the well-known port, and begins listening for connections. When a connection is received, the reverse proxy parses the JSON packet and determines what type of message it is. If it is a server setup packet (of type 1), the server is added to the policy dictionary. If it is a client request (of type 0), it looks in the policy dictionary for the client's requested policy, and forwards the request message to a server in the list. If a server isn't found, the reverse proxy sends an error message back to the client of type -1. When the reverse proxy receives the response from the server, it forwards the response back to the client and closes the connection with the client and server.<br/><br/>

## Limitations of the System

In order to attempt to find the maximum client load the system was able to withstand, I wrote a simple script to execute many client requests in a short amount of time. I started two servers for each of three policies, for a total of six servers. With these servers running, I was able to increase the client request load to about 120 requests per second with no loss of packets. This was the fastest my machine could actually initiate requests, so I did not increase the load further. As a final test, I decreased the server count to only one server for each policy, and the performance remained the same. These tests were done using the three sample packets included in this repository, however, and their payload is extremely small. If this payload were to be increased, the server processing time of the hash would increase, leading to a lower maximum load threshold. To prevent this issue, the maximum size of the packet payload has been restricted to 1024 bytes, and an error message results if the user attempts to send a payload larger than that.







