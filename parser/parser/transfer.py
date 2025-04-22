from dataclasses import dataclass


@dataclass
class PassportData:
    serial_number: int
    id: int
    firstname: str
    date_issue: str
    unit_code: int
    unit_name: str
    birthday_date: str
    snils_number: int
    is_male: bool
    birthplace: str
