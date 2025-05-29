from dataclasses import dataclass
from enum import Enum


class EmployerDataset(Enum):
    @classmethod
    @property
    def choises(cls):
        return [getattr(cls, i).value for i in dir(cls) if i[0].isupper()]


class PositionTitles(EmployerDataset):
    BASE_WORKER = "Разнорабочий"
    WORKER = "Рабочий"
    DRIVER = "Водитель"
    LOADER_DRIVER = "водитель погрузчика"
    TRUCK_DRIVER = "Водитель грузовика"
    HEAVY_TRUCK_DRIVER = "Водитель тяжелого грузовика"
    LOADER = "грузчик"
    BOSS = "Директор"
    SECTION_BOSS = "Директор отдела"
    PROGRAMMET = "техник-программист"


class Companies(EmployerDataset):
    WB = "7721546864"
    OZON = "7704217370"
    VSE_INSTRUMENTI = "7722753969"
    GRASS = "3445117986"
    YANDEX_MARKET = "7704357909"
    URENT = "9728139438"
    SDEK = "7720933109"
    BOXBERRY = "5029190794"
    X5 = "7733571872"
