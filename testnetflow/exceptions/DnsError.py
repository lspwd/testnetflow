class DnsError(Exception):
    def __init__(self, e):
        super(DnsError, self).__init__(e)
