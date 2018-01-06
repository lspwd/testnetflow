class SocketError(Exception):
    def __init__(self, e):
        super(SocketError, self).__init__(e)