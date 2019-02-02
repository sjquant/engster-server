class UnknownKeyword(Exception):

    def __init__(self, keyword, msg=None) -> None:
        if msg is None:
            msg = "{} is unknown keyword."
        super().__init__(msg)


class UnsupportedExtensionError(Exception):
    def __init__(self):
        msg = "The extension is not supported for this program."
        super().__init__(msg)


class InvalidDataFrameError(Exception):
    def __init__(self):
        msg = "The dataframe is invalid for this program."
        super().__init__(msg)


class UnknownKeyword(Exception):

    def __init__(self, keyword, msg=None) -> None:
        if msg is None:
            msg = "{} is unknown keyword."
        super().__init__(msg)


class InvalidModelError(Exception):
    def __init__(self, msg=None) -> None:
        if msg is None:
            msg = "It is Invalid Model"
        super().__init__(msg)
