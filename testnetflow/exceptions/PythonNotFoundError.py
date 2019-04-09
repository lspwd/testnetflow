class PythonNotFoundError(Exception):
    def __init__(self, e):
        super(PythonNotFoundError, self).__init__(e)
