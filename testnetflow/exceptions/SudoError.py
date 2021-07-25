class SudoError(Exception):
    def __init__(self, e):
        super(SudoError, self).__init__(e)
