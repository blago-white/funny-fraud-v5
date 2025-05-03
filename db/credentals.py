import random
import string
from itertools import groupby
from abc import ABCMeta, abstractmethod

import openpyxl
from rusgenderdetection import get_gender

from parser.parser.transfer import PassportData
from .base import SimpleConcurrentRepository
from .exceptions import CredentalsListEndedError

drop_dublicates = lambda s: "".join(c for c, _ in groupby(s))


class OwnerCredentialsRepository(metaclass=ABCMeta):
    _file_path: str

    def __init__(self, credentals_file_path: str = None):
        self._credentals_file = credentals_file_path or self._file_path

    @abstractmethod
    def get_next(self):
        pass

    @abstractmethod
    def restore_unused(self):
        pass


class OwnerTxtCredentalsContainer:
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


class OwnerXLSCredentalsContainer:
    _credentals: str
    _passport: PassportData

    def __init__(self, credentals: str):
        if len(credentals) < 11:
            self._raw_credentals = self._credentals = []
        else:
            self._raw_credentals = credentals
            self._credentals = [i.value for i in credentals]

    @property
    def raw_credentals(self):
        return self._raw_credentals

    def get_email(self):
        return f"{self.get_random_password()}@gmail.com"

    def get_passport_data(self) -> PassportData:
        date_issue = str(self._credentals[7]).split(" ")[0].replace("-", "")

        date_issue = date_issue[4:] + date_issue[:4]

        birthday_date = str(self._credentals[3]).split(" ")[0].replace("-", "")

        birthday_date = birthday_date[4:] + birthday_date[:4]

        return PassportData(
            serial_number=self._credentals[4].replace(" ", ""),
            id=self._credentals[5].replace(" ", ""),
            firstname=self._credentals[0].split(" ")[1],
            lastname=self._credentals[0].split(" ")[0],
            patronymic=self._credentals[0].split(" ")[2],
            date_issue=date_issue,
            unit_code=min(str(self._credentals[9]) or "", str(self._credentals[8]) or "", key=len).replace("-", ""),
            unit_name=self._credentals[6],
            birthday_date=birthday_date,
            snils_number=self._credentals[-1],
            is_male=get_gender(name=self._credentals[0].split(" ")[0]) == 1,
            birthplace=drop_dublicates(self._credentals[2].split("РОССИЯ,")[-1]).removeprefix(",").removesuffix(",")
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


class OwnerCredentalsTxtRepository(OwnerCredentialsRepository, SimpleConcurrentRepository):
    _file_path = "data/credentals.txt"

    @SimpleConcurrentRepository.locked()
    def get_next(self):
        with open(self._credentals_file, "r", encoding="utf-8") as file:
            credentals_list = file.readlines()

        with open(self._credentals_file, "w", encoding="utf-8") as file:
            if len(credentals_list) == 0:
                raise CredentalsListEndedError("Update the row sheet")

            iterations: int = 1

            while True:
                last_credentals = credentals_list[iterations-1]

                print(f"CREDENTALS RETRIEVE: {last_credentals}")

                if self._validate_credentals(credentals=OwnerTxtCredentalsContainer(credentals=last_credentals)):
                    file.writelines(credentals_list[iterations:])

                    print("SUCCESS RETRIEVED")

                    return OwnerTxtCredentalsContainer(credentals=last_credentals)

                iterations += 1

    @SimpleConcurrentRepository.locked()
    def restore_unused(self, credentals: OwnerTxtCredentalsContainer):
        with open(self._credentals_file, "r", encoding="utf-8") as file:
            credentals_file_list = file.readlines()

        with open(self._credentals_file, "w", encoding="utf-8") as file:
            credentals_file_list.insert(0, credentals.raw_credentals)

            file.writelines(credentals_file_list)

    def _validate_credentals(self, credentals: OwnerTxtCredentalsContainer):
        if len(credentals.get_passport_data().birthplace) < 4:
            return False

        return True


class OwnerCredentalsXLSRepository(OwnerCredentialsRepository, SimpleConcurrentRepository):
    _file_path = "data/credentials.xlsx"

    @SimpleConcurrentRepository.locked()
    def get_next(self) -> OwnerXLSCredentalsContainer:
        credentals_list_wb = openpyxl.load_workbook(filename=self._credentals_file)
        credentals_list = credentals_list_wb.active

        while True:
            columns = list(reversed(list(credentals_list.rows)))[0]

            if len(columns) < 4:
                credentals_list_wb.save(filename="data/credentials.xlsx")

                raise CredentalsListEndedError("Update credentals sheet")

            if self._validate_credentals(credentals=OwnerXLSCredentalsContainer(credentals=columns)):
                print("SUCCESS RETRIEVED")

                credentals_list.delete_rows(idx=len(list(credentals_list.rows)))

                credentals_list_wb.save(filename="data/credentials.xlsx")

                return OwnerXLSCredentalsContainer(credentals=columns)

            credentals_list.delete_rows(idx=len(list(credentals_list.rows)))

    @SimpleConcurrentRepository.locked()
    def restore_unused(self, credentals: OwnerXLSCredentalsContainer):
        wb = openpyxl.load_workbook(filename=self._credentals_file)
        ws = wb.active

        ws.append(credentals.raw_credentals)

        credentals_list_wb.save(filename="data/credentials.xlsx")

    def _validate_credentals(self, credentals: OwnerXLSCredentalsContainer):
        print(len(credentals.raw_credentals))
        if len(credentals.raw_credentals) < 11:
            print("A")
            return False

        if len(credentals.get_passport_data().unit_code) != 6:
            print("B")
            return False

        if len(credentals.get_passport_data().birthplace) < 4:
            print("C")
            return False

        return True
