class CredentalsListEndedError(Exception):
    pass


class ProxyNotExists(Exception):
    def __repr__(self):
        return f"{self.__class__.__name__}(\"Set Up proxy please!\")"

    def __str__(self):
        return f"Set Up proxy please!"


class ProxyFormatError(Exception):
    pass
