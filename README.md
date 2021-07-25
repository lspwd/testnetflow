# testnetflow

The main purpose of testnetflow is to assess the network path status between a cleint and a server, discovering if TCP sockets exposed by the servers are reachable by the tcp clients. 
Testnetflow is useful in on-prem layered environments, where you don't actually know the status of tcp networking flows up front. 
This is designed to be installed in one single server, which will orchestrate through paramiko library the ssh connections towards clients and servers, and will collect connectivity results sent by the clients, while connecting to their respective list of servers. 

The only pre-requirement is that you must have SSH(TCP/22) port open from the orchestrator to clients and servers to run testnetflow.

Testnetflow leverages threads help.
All sockets will be started by the server thread pool, on the destination boxes. Testnetflow is not assuming that you will have destination server sockeet in place .
Sockets will be started on the destination servers only if they won't be found alive. 

The main configuration properties file describes the relationship 1 to N , between the client and a list of server ( with a list of sockets to test ). 
Testnetflow, upon startup, reads config file and makes the following actions:l

1) ( server thread pool ) connect to all servers via ssh to bring up sockets 
2) ( client thread pool ) wait from servers, for the sockets startup event, then start the connectivity tests 
3) ( reporting thread pool ) wrap up assessment results from clients

