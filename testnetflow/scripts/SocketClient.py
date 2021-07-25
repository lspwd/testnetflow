#!/usr/bin/python

from __future__ import print_function

import socket
import sys
import uuid


class TimeoutError(Exception):
    def __init__(self, ex1):
        super(TimeoutError, self).__init__(ex1)


class SocketError(Exception):
    def __init__(self, ex2):
        super(SocketError, self).__init__(ex2)


class SocketClient:
    def __init__(self, address, dstport, conntimeout):
        self.conntimeout = float(conntimeout)
        self.address = address
        self.dstport = int(dstport)

    def connect(self, testprobe):

        client = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(self.conntimeout)
            client.connect((self.address, self.dstport))
            client.send(testprobe)
            return client.recv(1024)

        except socket.timeout as e1:
            raise TimeoutError(e1)

        except socket.error as e2:
            raise SocketError(e2)

        except Exception as ex:
            raise RuntimeError(ex)

        finally:
            try:
                if hasattr(client, "close"):
                    client.close()
            except NameError:
                pass

    def connectP2p(self):
        client = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(self.conntimeout)
            client.connect((self.address, self.dstport))

        except socket.timeout as e1:
            raise TimeoutError(e1)

        except socket.error as e2:
            raise SocketError(e2)

        except Exception as ex:
            raise RuntimeError(ex)

        finally:
            try:
                if hasattr(client, "close"):
                    client.close()
            except NameError:
                pass


    def serverClose(self):

        client = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(self.conntimeout)
            client.connect((self.address, self.dstport))
            client.send("close")

        except socket.timeout as e1:
            raise TimeoutError(e1)

        except socket.error as e2:
            raise SocketError(e2)

        except Exception as ex:
            raise RuntimeError(ex)

        finally:
            try:
                if hasattr(client, "close"):
                    client.close()
            except NameError:
                pass


def main():

    if len(sys.argv) != 6:
        print(len(sys.argv))
        print(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    timeout = sys.argv[3]
    deployed = (sys.argv[4])
    close = (sys.argv[5])

    if deployed == "False":
        deployed = False

    if close == "False":
        close = False

    socketClient = SocketClient(ip, port, timeout)

    if deployed:
        request = str(uuid.uuid4())
        try:
            # print(request)
            response = socketClient.connect(str(request))
            # print(response)
            if request == response:
                print("The Connection to " + ip + ":" + str(port) + " has been tested successfully!")
            else:
                print("ERROR: The received payload from the remote endpoint is different " + ip, file=sys.stderr)
        except (SocketError, TimeoutError, RuntimeError) as e:
            print("ERROR: Exception caught while connecting to the remote endpoint "
                  + ip + " --- " + str(e), file=sys.stderr)
    else:
        try:
            # print(request)
            socketClient.connectP2p()
            # print(response)
            print("The Connection to " + ip + ":" + str(port) + " has been tested successfully!")
        except (SocketError, TimeoutError, RuntimeError) as e:
            print("ERROR: Exception caught while connecting to the remote endpoint "
                  + ip + " --- " + str(e), file=sys.stderr)

    if close:
        try:
            socketClient.serverClose()
            print("The Connection to " + ip + ":" + str(port) + " has been closed successfully!")
        except (SocketError, TimeoutError, RuntimeError, Exception) as e:
            print("ERROR: Exception caught while closing to the remote server " + ip + " --- " + str(e), file=sys.stderr)

if __name__ == '__main__':
    main()
