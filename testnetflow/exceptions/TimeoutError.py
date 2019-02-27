class TimeoutError(Exception):
    def __init__(self, e):
        super(TimeoutError, self).__init__(e)
