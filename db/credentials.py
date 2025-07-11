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

    @property
    def file_path(self) -> str:
        return self._file_path

    @abstractmethod
    def get_next(self):
        pass

    @abstractmethod
    def restore_unused(self):
        pass


class OwnerTxtCredentialsContainerLegacy:
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


# class OwnerTxtCredentialsContainer:
#     _credentals: str
#     _passport: PassportData
#
#     def __init__(self, credentals: str):
#         self._raw_credentals = credentals
#         self._credentals = credentals.split(" | ")
#
#     @property
#     def raw_credentals(self):
#         return self._raw_credentals
#
#     def get_email(self):
#         return f"{self.get_random_password()}@gmail.com"
#
#     def get_passport_data(self) -> PassportData:
#         return PassportData(
#             serial_number=self._passport_properties[0],
#             id=self._passport_properties[1],
#             firstname=self._name[1],
#             lastname=self._name[0],
#             patronymic=self._name[2],
#             date_issue=self._passport_properties[2],
#             unit_code=self._passport_properties[3],
#             unit_name=self._passport_properties[4],
#             birthday_date=self._birthday,
#             snils_number="".join(list(filter(lambda c: c.isdigit(), self._credentals[2]))),
#             is_male="ПОЛ: M" in self._credentals[-7],
#             birthplace=self._credentals[-2].replace("Адрес прописки: ", "")
#         )
#
#     @property
#     def _name(self) -> tuple[str, str, str]:
#         print(self._credentals[1].replace("ФИО: ", "").removesuffix(" ").split(" "))
#         return self._credentals[1].replace("ФИО: ", "").removesuffix(" ").split(" ")
#
#     @property
#     def _birthday(self) -> str:
#         return "".join(list(filter(lambda c: c.isdigit(), self._credentals[-8])))
#
#     @property
#     def _snils(self):
#         return "".join(list(filter(lambda c: c.isdigit(), self._credentals[2])))
#
#     @property
#     def _passport_properties(self):
#         passport_numbers = "".join(list(filter(lambda c: c.isdigit(), self._credentals[3])))
#
#         return passport_numbers[:4], passport_numbers[4:10], passport_numbers[10:18], passport_numbers[18:24], self._credentals[3].split("\"issuedBy\":\"")[-1].split("\",\"")[0]
#
#     @staticmethod
#     def get_random_password():
#         return "".join(
#             [random.choice(
#                 random.choice([
#                     string.ascii_lowercase,
#                     string.ascii_uppercase
#                 ])
#             ) for _ in range(9)] + ["-"] + [random.choice(string.digits)]
#         )
#


class OwnerTxtCredentialsContainer:
    _credentals: str
    _passport: PassportData

    def __init__(self, credentals: str):
        self._raw_credentals = credentals

        full_name = credentals.split(";")[0]

        credentals = credentals.replace(";", "")

        self._credentals = full_name, credentals

    @property
    def raw_credentals(self):
        return self._raw_credentals

    def get_email(self):
        return f"{self.get_random_password()}@gmail.com"

    def get_passport_data(self) -> PassportData:
        return PassportData(
            serial_number=self._passport_properties[0],
            id=self._passport_properties[1],
            firstname=self._name[1],
            lastname=self._name[0],
            patronymic=self._name[2],
            date_issue=self._passport_properties[2],
            unit_code=self._passport_properties[3],
            unit_name=self._passport_properties[4],
            birthday_date=self._birthday,
            snils_number=self._snils,
            is_male=not (get_gender(name=self._credentals[0].split(" ")[0]) == 0),
            birthplace=self._credentals[-1].split("Прописка - ")[-1].split(" ИНН - ")[0]
        )

    @property
    def _name(self) -> tuple[str, str, str]:
        return self._credentals[0].split(" ")

    @property
    def _birthday(self) -> str:
        return self._credentals[-1].split("Дата рождения - ")[-1].split(" ")[0]

    @property
    def _snils(self):
        return self._credentals[-1].split("СНИЛС - ")[-1].replace("-", "").replace(" ", "")

    @property
    def _passport_properties(self):
        serial_number = self._credentals[-1].split("Паспорт - ")[-1].split(" ")[0]
        date_issue = self._credentals[-1].split("Дата выдачи - ")[-1].split(" ")[0]
        unit_name = self._credentals[-1].split("Кем выдан - ")[-1].split(" Код подразделения - ")[0]
        unit_code = self._credentals[-1].split("Код подразделения - ")[-1].split(" ")[0]

        return serial_number[:4], serial_number[4:], date_issue, unit_code, unit_name

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


class OwnerXLSCredentialsContainer:
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


class OwnerCredentialsTxtRepository(OwnerCredentialsRepository, SimpleConcurrentRepository):
    _file_path = "data/credentials.txt"

    @SimpleConcurrentRepository.locked()
    def get_next(self):
        with open(self._credentals_file, "r", encoding="utf-8", errors="replace") as file:
            credentals_list = file.readlines()

        with open(self._credentals_file, "w", encoding="utf-8", errors="replace") as file:
            if len(credentals_list) == 0:
                raise CredentalsListEndedError("Update the row sheet")

            iterations: int = 1

            while True:
                last_credentals = credentals_list[iterations-1]

                print(f"CREDENTALS RETRIEVE: {last_credentals}")

                if self._validate_credentals(credentals=OwnerTxtCredentialsContainer(credentals=last_credentals)):
                    file.writelines(credentals_list[iterations:])

                    print("SUCCESS RETRIEVED")

                    return OwnerTxtCredentialsContainer(credentals=last_credentals)

                iterations += 1

    @SimpleConcurrentRepository.locked()
    def restore_unused(self, credentals: OwnerTxtCredentialsContainer):
        with open(self._credentals_file, "r", encoding="utf-8", errors="replace") as file:
            credentals_file_list = file.readlines()

        with open(self._credentals_file, "w", encoding="utf-8", errors="replace") as file:
            credentals_file_list.insert(0, credentals.raw_credentals)

            file.writelines(credentals_file_list)

    def _validate_credentals(self, credentals: OwnerTxtCredentialsContainer):
        if len(credentals.get_passport_data().birthplace) < 4:
            return False

        return True


class OwnerCredentialsXLSRepository(OwnerCredentialsRepository, SimpleConcurrentRepository):
    _file_path = "data/credentials.xlsx"

    @SimpleConcurrentRepository.locked()
    def get_next(self) -> OwnerXLSCredentialsContainer:
        credentals_list_wb = openpyxl.load_workbook(filename=self._credentals_file)
        credentals_list = credentals_list_wb.active

        while True:
            columns = list(reversed(list(credentals_list.rows)))[0]

            if len(columns) < 4:
                credentals_list_wb.save(filename=self._credentals_file)

                raise CredentalsListEndedError("Update credentals sheet")

            if self._validate_credentals(credentals=OwnerXLSCredentialsContainer(credentals=columns)):
                print("SUCCESS RETRIEVED")

                credentals_list.delete_rows(idx=len(list(credentals_list.rows)))

                credentals_list_wb.save(filename=self._credentals_file)

                return OwnerXLSCredentialsContainer(credentals=columns)

            credentals_list.delete_rows(idx=len(list(credentals_list.rows)))

    @SimpleConcurrentRepository.locked()
    def restore_unused(self, credentals: OwnerXLSCredentialsContainer):
        wb = openpyxl.load_workbook(filename=self._credentals_file)
        ws = wb.active

        ws.append(credentals.raw_credentals)

        credentals_list_wb.save(filename=self._credentals_file)

    def _validate_credentals(self, credentals: OwnerXLSCredentialsContainer):
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


# Грищенко Николай Алексеевич; Дата рождения - 12.01.1986 Серия и номер - 0306321453 Дата выдачи - 04.03.2006 Место рождения - Краснодарский край Курганинский р-н Курганинск г. Кем выдан - ПВС ОВД Курганинского р-на Краснодарского края Код подразделения - 232040 Прописка - Курганинский р-н Курганинск г. ул.Чайковского ул. д.52 ИНН - 233910427348 СНИЛС - 133-045-049 10

# Грищенко Николай Алексеевич;
# Дата рождения - 12.01.1986
# Серия и номер - 0306321453
# Дата выдачи - 04.03.2006
# Место рождения - Краснодарский край Курганинский р-н Курганинск г.
# Кем выдан - ПВС ОВД Курганинского р-на Краснодарского края
# Код подразделения - 232040
# Прописка - Курганинский р-н Курганинск г. ул.Чайковского ул. д.52
# ИНН - 233910427348
# СНИЛС - 133-045-049 10
