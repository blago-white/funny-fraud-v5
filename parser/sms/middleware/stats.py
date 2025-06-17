from ..exceptions import NumberGettingException


class SmsRequestsStatMiddleware:
    _SUCCESS_RECEIVE = 0
    _FAIL_RECEIVE = _SUCCESS_RECEIVE
    _CANCELED = _FAIL_RECEIVE

    _FROZEN = False

    _CANCELED_IDS = set()

    @property
    def all_stats(self):
        return self.success_receive, self.failed_receive, self.canceled

    @property
    def success_receive(self):
        return self._SUCCESS_RECEIVE

    @property
    def failed_receive(self):
        return self._FAIL_RECEIVE

    @property
    def canceled(self):
        return self._CANCELED

    @classmethod
    def freeze_phone_receiving(cls):
        # cls._FROZEN = True
        pass

    @classmethod
    def allow_phone_receiving(cls):
        cls._FROZEN = False

    @classmethod
    def counter_receive_phone(cls, func):
        def wrapped(*args, **kwargs):
            if cls._FROZEN:
                raise NumberGettingException("NUMBER RECEIVING IS FROZEN NOW")

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                cls._FAIL_RECEIVE += 1

                raise e

            if not all(result):
                cls._FAIL_RECEIVE += 1
            else:
                cls._SUCCESS_RECEIVE += 1

            return result

        return wrapped

    @classmethod
    def counter_cancel_phone(cls, func):
        def wrapped(*args, **kwargs):
            if not kwargs.get("phone_id", -1) in cls._CANCELED_IDS:
                cls._CANCELED += 1
                cls._CANCELED_IDS.add(kwargs.get("phone_id", -1))

            return func(*args, **kwargs)

        return wrapped
