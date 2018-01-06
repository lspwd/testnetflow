class ConfiguationError(Exception):
    def __init__(self, e):
        super(ConfiguationError, self).__init__(e)
