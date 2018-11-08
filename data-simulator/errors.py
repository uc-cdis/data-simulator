"""
TODO
"""

class UserError(Exception):
    def __init__(self, message):
        super(UserError, self).__init__(message)

class DictionaryError(Exception):
    def __init__(self, message):
        super(DictionaryError, self).__init__(message)
