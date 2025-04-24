import random
import string
from dataclasses import dataclass

from russian_names import RussianNames

from parser.parser.transfer import PassportData

from .exceptions import CredentalsListEndedError
from .base import SimpleConcurrentRepository


class OwnerCredentalsContainer:
    _credentals: str
    _passport: PassportData

    def __init__(self, credentals: str):
        self._raw_credentals = credentals
        self._credentals = credentals.replace("'", "").split(";")

    @property
    def raw_credentals(self):
        return self._raw_credentals

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


class OwnerCredentalsRepository(SimpleConcurrentRepository):
    def __init__(self, credentals_file_path: str = "data/credentals.txt"):
        self._credentals_file = credentals_file_path
        super().__init__()

    @SimpleConcurrentRepository.locked()
    def get_next(self):
        with open(self._credentals_file, "r", encoding="utf-8") as file:
            credentals_list = file.readlines()

        print(credentals_list)

        with open(self._credentals_file, "w", encoding="utf-8") as file:
            if len(credentals_list) == 1:
                raise CredentalsListEndedError("Update the row sheet")

            while True:
                last_credentals = credentals_list[0]

                if self._validate_credentals(credentals=Cre)

            file.writelines(credentals_list[1:])

        return OwnerCredentalsContainer(credentals=last_credentals)

    @SimpleConcurrentRepository.locked()
    def restore_unused(self, credentals: OwnerCredentalsContainer):
        with open(self._credentals_file, "r", encoding="utf-8") as file:
            credentals_file_list = file.readlines()

        with open(self._credentals_file, "w", encoding="utf-8") as file:
            credentals_file_list.insert(0, credentals.raw_credentals)

            file.writelines(credentals_file_list)

    def _validate_credentals(self, credentals: OwnerCredentalsContainer):
        if len(credentals.get_passport_data().birthplace) < 4:
            return False

        return True
