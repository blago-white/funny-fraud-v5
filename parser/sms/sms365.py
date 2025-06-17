import os

import requests

from .exceptions import NumberGettingException
from .middleware import SmsRequestsStatMiddleware, \
    SmsServiceThrottlingMiddleware


class SMS365Service:
    _apikey: str

    SMS_TIMEOUT = 60*1.5

    _API_ROUTES = {
        "balance": "https://365sms.ru/stubs/handler_api.php?"
                   "api_key={api}&action=getBalance",
        "number": "https://365sms.ru/stubs/handler_api.php"
                  "?api_key={api}&action=getNumber"
                  "&service=wd&operator={oper}&country=0",
        "set-status": "https://365sms.ru/stubs/handler_api.php?"
                      "api_key={api}&action=setStatus&status=8&id={id}",
        "get-code": "https://365sms.ru/stubs/handler_api.php?"
                    "api_key={api}&action=getStatus&id={id}"
    }

    _OPERATORS = [
        "mts",
        "megafon",
        "rostelecom",
        "tele2",
        "tinkoff",
        "yota",
        "mtt_virtual",
        "beeline",
    ]

    def __init__(self, apikey: str = os.environ.get("SMS_SERVICE_APIKEY")):
        self._apikey = apikey or os.environ.get("SMS_SERVICE_APIKEY")

    @property
    def balance(self) -> float:
        response = requests.get(
            self._API_ROUTES.get("balance").format(api=self._apikey)
        )

        if not response.ok:
            raise ValueError("Error retrieve balance")

        data: str = response.text

        return float(data.split(":")[-1])

    @SmsServiceThrottlingMiddleware.throttle(rps=2, space="365")
    @SmsRequestsStatMiddleware.counter_cancel_phone
    def cancel(self, phone_id: int):
        response = requests.get(
            self._API_ROUTES.get("set-status").format(
                api=self._apikey,
                id=str(phone_id)
            )
        )

        text = response.text

        if (not response.ok) or (text != "ACCESS_CANCEL"):
            print(f"Error canceling number rent: {text}")
            # raise ValueError()

        print("CANCELED")

    def check_code(self, phone_id: int) -> str | None:
        response = requests.get(
            self._API_ROUTES.get("get-code").format(
                api=self._apikey,
                id=str(phone_id)
            )
        )

        if not response.ok:
            return None

        response = response.text

        if "STATUS_OK" in response:
            return response.split(":")[-1]

    @SmsServiceThrottlingMiddleware.throttle(rps=2, space="365")
    @SmsRequestsStatMiddleware.counter_receive_phone
    def get_number(self) -> list[int, int]:
        text = None

        for oper in self._OPERATORS:
            print(self._API_ROUTES.get("number").format(
                api=self._apikey, oper=oper
            ))

            response = requests.get(
                self._API_ROUTES.get("number").format(
                    api=self._apikey, oper=oper
                )
            )

            text = response.text
            ok = response.ok

            if (not ok) and text != "NO_NUMBERS":
                raise NumberGettingException(text)

            elif (not ok) and text == "NO_NUMBERS":
                continue

            if ok:
                break

        if not ("ACCESS_NUMBER" in text):
            raise NumberGettingException(
                f"Not correct response: {text}"
            )

        number_data = [int(i) for i in text.split(":")[1:]]

        return number_data[0], str(number_data[1])
