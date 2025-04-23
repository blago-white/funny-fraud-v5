import random
import string
from dataclasses import dataclass

from russian_names import RussianNames

from .transfer import PassportData


class OwnerCredentalsRepository:
    _credentals: str
    _passport: PassportData

    def __init__(self, credentals: str):
        self._credentals = credentals.replace("'", "").split(";")

    def get_email(self):
        return self._credentals[23].replace(" ", "") or f"{self.get_random_password()}@gmail.com"

    def get_passport_data(self) -> PassportData:
        return PassportData(
            serial_number=self._credentals[17],
            id=self._credentals[18],
            firstname=self._credentals[4],
            lastname=self._credentals[5],
            patronymic=self._credentals[6],
            date_issue=self._credentals[21],
            unit_code=self._credentals[19],
            unit_name=self._credentals[20],
            birthday_date=self._credentals[11].replace(".", ""),
            snils_number=self._credentals[12],
            is_male=self._credentals[10] == "MALE",
            birthplace=self._credentals[14]
        )

    @staticmethod
    def get_random_password():
        return "".join(
            [random.choice(
                random.choice([
                    string.ascii_lowercase,
                    string.ascii_uppercase
                ])
            ) for _ in range(9)] + ["-"] + [random.choice(string.digits)]
        )


@dataclass
class PaymentsCardData:
    number: str
    date: str
    cvc: str

    @classmethod
    def generate(cls, card: str):
        return cls(*card.split("@"))
