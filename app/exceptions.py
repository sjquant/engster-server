class UnsupportedExtension(Exception):
    def __init__(self, msg="The extension is not supported for this program."):
        super().__init__(msg)


class InvalidDataFrame(Exception):
    def __init__(self, msg="The dataframe is invalid for this program."):
        super().__init__(msg)


class DataDoesNotExist(Exception):
    def __init__(self, msg="Data does not exist."):
        super().__init__(msg)
