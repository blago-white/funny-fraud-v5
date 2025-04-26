from aiogram.fsm.state import StatesGroup, State


class SessionForm(StatesGroup):
    set_count_complete_requests = State()
    set_ref_link = State()
    approve_session = State()


class GologinApikeySettingForm(StatesGroup):
    wait_apikey = State()


class SmsServiceApikeySettingForm(StatesGroup):
    wait_apikey = State()


class ProxySettingForm(StatesGroup):
    wait_base_proxy = State()
