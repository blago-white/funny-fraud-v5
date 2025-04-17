import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

from . import utils, exceptions


class OfferInitializerParser:
    _form_already_inited: bool = False
    _card_data_already_entered: bool = False
    _card_data_page_path: str = None
    _account_not_logined: bool = None

    _OWNER_DATA_FIELDS_IDS = [
        "input[name='firstName']",
        "input[name='lastName']",
        "input[name='dob']",
        "input[name='password']",
        "input[name='confirmPassword']",
        "input[name='email']",
    ]

    _PAYMENT_CARD_FIELDS_IDS = [
        "input[id='pan']",
        "input[id='expiry']",
        "input[id='cvc']"
    ]

    def __init__(
            self, payments_card: utils.PaymentsCardData,
            driver: Chrome,
            owner_data_generator: utils.OwnerCredentalsGenerator = None):
        self._driver = driver

        self._payments_card = payments_card

        if type(payments_card) is str:
            self._payments_card = utils.PaymentsCardData.generate(
                self._payments_card
            )

        self._owner_data_generator = (owner_data_generator or
                                      utils.OwnerCredentalsGenerator())

    @property
    def driver(self):
        return self._driver

    def register(self, url: str, phone: str, _retry: bool = False):
        self._driver.get(url=url)

        self._click_get_account()

        self._select_registration_provider()

        self._enter_phone(phone=phone)

    def enter_registration_otp(self, otp: int | str):
        self._enter_registration_otp(otp=otp)

        self._enter_password()

    def _enter_password(self):
        WebDriverWait(self._driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.ID, "simple-registration-input-new-password")
            )
        )

        password_field = self._driver.find_element(
            By.ID, "simple-registration-input-new-password"
        )

        password_field.click()

        password_field.send_keys(
            self._owner_data_generator.get_random_password()
        )

    def _enter_registration_otp(self, otp: int | str):
        otp = str(otp)

        WebDriverWait(self._driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.ID, "simple-registration-code-input-1")
            )
        )

        for number, otp_char in enumerate(otp, start=1):
            self._driver.find_element(By.ID, f"simple-registration-code-input-{number}").send_keys(
                otp_char
            )

            time.sleep(.25)

        WebDriverWait(self._driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".set-password-form__title.title")
            )
        )

    def _enter_phone(self, phone: str):
        try:
            WebDriverWait(self._driver, 5).until(
                expected_conditions.element_to_be_clickable(
                    (By.ID, "simple-registration-input-phone")
                )
            )
        except:
            raise exceptions.TraficBannedError()

        phone_input = self._driver.find_element(
            By.ID, "simple-registration-input-phone"
        )

        phone_input.click()

        time.sleep(0.1)

        phone_input.send_keys(phone)

        time.sleep(0.5)

        self._driver.find_element(
            By.ID, "simple-registration-button-add-phone"
        ).click()

        self._check_number_entered(phone=phone)

    def _check_number_entered(self, phone: str):
        phone_label = self._driver.find_element(By.CSS_SELECTOR, 'span[t-text="phone"]')

        for phone_symbol in phone:
            if phone_symbol not in phone_label.text:
                raise ValueError("Phone not entered")

    def _click_get_account(self):
        try:
            WebDriverWait(self._driver, 40).until(
                expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#__next > div.Layout_layout__YlB83.Layout_noPadding__MfDWP > main > section.QuestionnaireProductSelection_section__sM_kf > div > div:nth-child(1) > div.AmountForm_formCard__OG3u6 > button")
                )
            )
        except:
            raise exceptions.TraficBannedError()

        self._driver.find_element(
            By.CLASS_NAME, "#__next > div.Layout_layout__YlB83.Layout_noPadding__MfDWP > main > section.QuestionnaireProductSelection_section__sM_kf > div > div:nth-child(1) > div.AmountForm_formCard__OG3u6 > button"
        ).click()

    def _select_registration_provider(self):
        try:
            WebDriverWait(self._driver, 10).until(
                expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".new-ui-button -secondary -m -stretch")
                )
            )
        except:
            raise exceptions.TraficBannedError()

        self._driver.find_element(
            By.CSS_SELECTOR, ".new-ui-button -secondary -m -stretch"
        ).click()
