class TraficBannedError(Exception):
    used_phone_id: int | None
    used_phone_number: str | None

    def __init__(self, used_phone_id: int = None, used_phone_number: str = None):
        self.used_phone_number = used_phone_number
        self.used_phone_id = used_phone_id


class RegistrationSMSTimeoutError(Exception):
    pass


class BadSMSService(Exception):
    pass


class InitializingError(TraficBannedError):
    crude_exception: Exception

    def __init__(self, *args, crude_exception: Exception = None, **kwargs):
        self.crude_exception = crude_exception

        super().__init__(*args, **kwargs)
