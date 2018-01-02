class SudoNotFoundError(Exception):
    def __init__(self, e):
        super(SudoNotFoundError, self).__init__(e)
