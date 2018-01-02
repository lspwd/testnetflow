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


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print(len(sys.argv))
        print(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    timeout = sys.argv[3]

    socketClient = SocketClient(ip, port, timeout)
    request = str(uuid.uuid4())
    try:
        # print(request)
        response = socketClient.connect(str(request))
        # print(response)
        if request == response:
            print("The Connection to " + ip + ":" + port + " has been tested successfully!")
        else:
            print("ERROR: The received payload from the remote endpoint is different " + ip, file=sys.stderr)
    except (SocketError, TimeoutError, RuntimeError) as e:
        print("ERROR: Exception caught while connecting to the remote endpoint "
              + ip + " --- " + str(e), file=sys.stderr)
