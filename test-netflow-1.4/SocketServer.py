#!/usr/bin/python

from __future__ import print_function

import socket
import sys
from datetime import datetime


class TimeoutError(Exception):
    def __init__(self, ex1):
        super(TimeoutError, self).__init__(ex1)


class SocketError(Exception):
    def __init__(self, ex2):
        super(SocketError, self).__init__(ex2)


class SocketServer:
    def __init__(self, srvip, srvport, srvtimeout, listenBacklog):
        self.ip = srvip
        self.port = int(srvport)
        self.timeout = float(srvtimeout)
        self.listenBacklog = int(listenBacklog)

    def getListeningSocket(self):

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set fast reuse of the the socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(self.timeout)
            s.bind((self.ip, self.port))
            s.listen(self.listenBacklog)
            return s

        except socket.timeout as ex1:
            raise TimeoutError(ex1)
        except socket.error as ex2:
            raise SocketError(ex2)
        except Exception as ex:
            raise RuntimeError(ex)

    def acceptClientRequest(self, listenSocket):
        try:
            acceptedSocket, ipcaller = listenSocket.accept()
            return acceptedSocket
        except socket.timeout as ex1:
            raise TimeoutError(ex1)
        except socket.error as ex2:
            raise SocketError(ex2)
        except Exception as ex:
            raise RuntimeError(ex)

    def receiveClientRequest(self, acceptedSocket):
        try:
            clientrequest = acceptedSocket.recv(1024)
            return clientrequest
        except Exception as ex1:
            raise RuntimeError(ex1)

    def sendServerResponse(self, acceptedSocket, response):
        try:
            acceptedSocket.send(response)
        except Exception as ex1:
            raise SocketError(ex1)

    def closeListeningSocket(self, listenSocket):
        try:
            if hasattr(listenSocket, "close"):
                listenSocket.close()
        except Exception as ex1:
            raise SocketError(ex1)

    def closeAcceptedSocket(self, acceptedSocket):
        try:
            if hasattr(acceptedSocket, "close"):
                acceptedSocket.close()
        except Exception as ex1:
            raise SocketError(ex1)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(len(sys.argv))
        print(sys.argv[0])
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    timeout = sys.argv[3]

    counter = 0
    backlog = 25

    try:

        socketServer = SocketServer(ip, port, timeout, backlog)
        listeningSocket = socketServer.getListeningSocket()
        counter = 0
        while True:
            try:
                newacceptedSocket = socketServer.acceptClientRequest(listeningSocket)
                request = socketServer.receiveClientRequest(newacceptedSocket)
                print(str(datetime.now())[:-3] + " --- Processing client request: " + request)
                socketServer.sendServerResponse(newacceptedSocket, request)
                counter = 0
                newacceptedSocket.close()
                print(str(datetime.now())[:-3] + " --- Request has been successfully sent!")
            except TimeoutError as e1:
                counter += 1
                print("Hit timeout: " + str(counter))
            except SocketError as e2:
                print("Hit a Socket Exception : " + str(e2))
                sys.exit(1)
            finally:
                if counter >= 10:
                    print("Closing connection!")
                    try:
                        if hasattr(newacceptedSocket, "close"):
                            socketServer.closeAcceptedSocket(newacceptedSocket)
                    except NameError as e:
                        pass
                    socketServer.closeListeningSocket(listeningSocket)
                    exit(2)

    except (SocketError, TimeoutError, RuntimeError) as e:
        print("Exception type caught: " + str(type(e)) + " " + str(e), file=sys.stderr)
        exit(1)
