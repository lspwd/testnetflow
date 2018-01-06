class FileNotFoundError(Exception):
    def __init__(self, e):
        super(FileNotFoundError, self).__init__(e)
