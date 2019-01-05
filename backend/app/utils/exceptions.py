class UnknownKeyword(Exception):

    def __init__(self, keyword, msg=None) -> None:
        if msg is None:
            msg = "{} is unknown keyword."
        super().__init__(msg)
