class UnsupportedExtensionError(Exception):
    def __init__(self):
        msg = 'The extension is not supported for this program.'
        super().__init__(msg)


class InvalidDataFrameError(Exception):
    def __init__(self):
        msg = 'The dataframe is invalid for this program.'
        super().__init__(msg)
