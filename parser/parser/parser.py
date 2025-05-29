import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

from db import credentials
from . import exceptions, data


class OfferInitializerParser:
    _form_already_inited: bool = False
    _credentials: credentials.OwnerTxtCredentialsContainer = None

    def __init__(
            self, driver: Chrome,
            owner_data_generator: credentials.OwnerCredentialsTxtRepository = None):
        self._driver = driver

        self._owner_data_generator = (
            owner_data_generator
        )

    @property
    def driver(self):
        return self._driver

    @property
    def _owner_credentials(self):
        if self._credentials:
            return self._credentials

        self._credentials = self._owner_data_generator.get_next()

        return self._credentials

    def register(self, url: str, phone: str, _retry: bool = False):
        if not self._form_already_inited:
            self._driver.get(url=url)

            self._click_get_account()

            self._select_registration_provider()
        else:
            self._back_to_entering_phone(new_phone=phone)

        self._enter_phone(phone=phone)

        self._form_already_inited = True

    def enter_registration_otp(self, otp: int | str):
        self._enter_registration_otp(otp=otp)

        self._enter_password()

        self._enter_owner_primary_data()

    def enter_approval_otp(self, otp: str):
        WebDriverWait(self._driver, 2.5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".new-ui-input-base__field.-small")
            )
        )

        approval_otp_field = self._driver.find_element(
            By.CSS_SELECTOR, ".new-ui-input-base__field.-small"
        )

        for s in otp:
            approval_otp_field.send_keys(s)
            time.sleep(.5)

    def enter_owner_passport_data(self):
        WebDriverWait(self._driver, 50).until(
            expected_conditions.element_to_be_clickable(
                (By.CLASS_NAME, "new-ui-radio")
            )
        )

        self._driver.find_elements(By.CLASS_NAME, "new-ui-radio")[1].click()

        time.sleep(.5)

        passport = self._owner_credentials.get_passport_data()

        if not passport.is_male:
            self._driver.find_element(By.ID, "personal-form_gender-female")

        self._driver.find_element(By.ID,
                                  "personal-form_input-series").send_keys(
            passport.serial_number)
        self._driver.find_element(By.ID,
                                  "personal-form_input-number").send_keys(
            passport.id)

        time.sleep(.5)

        self._driver.find_element(By.ID, "personal-form_input-date").click()
        self._driver.find_element(By.ID, "personal-form_input-date").send_keys(
            passport.date_issue)

        time.sleep(.5)

        self._driver.find_element(By.ID, "personal-form_input-code").click()
        self._driver.find_element(By.ID, "personal-form_input-code").send_keys(
            passport.unit_code)

        print("1")

        time.sleep(3)

        self._driver.find_elements(By.CLASS_NAME, "ui-dropdown-option")[
            0].click()

        time.sleep(.5)

        print("2")

        self._driver.find_element(By.ID,
                                  "personal-form_input-birthdate").click()
        self._driver.find_element(By.ID,
                                  "personal-form_input-birthdate").send_keys(
            passport.birthday_date)

        print("3")

        time.sleep(.5)

        self._driver.find_element(By.ID,
                                  "personal-form_input-birthplace").click()
        self._driver.find_element(By.ID,
                                  "personal-form_input-birthplace").send_keys(
            passport.birthplace)

        print("4")

        time.sleep(.5)

        registration_field = self._driver.find_element(By.ID, "personal-form_input-registrationAddress")

        print("5")

        registration_field.click()
        registration_field.send_keys(passport.birthplace)

        print("6")

        time.sleep(5)

        # self._driver.find_elements(By.CLASS_NAME, "ui-dropdown-option")[6].click()

        # time.sleep(5)

        def dropdown_choices_exists():
            try:
                if len(self._driver.find_elements(By.CLASS_NAME, "ui-dropdown-option")) > 1:
                    return True
                raise ValueError
            except:
                return False

        while not dropdown_choices_exists():
            registration_field.send_keys(Keys.ARROW_DOWN)
            registration_field.send_keys(Keys.ARROW_DOWN)

            time.sleep(1)

            registration_field.send_keys(Keys.BACKSPACE)

            time.sleep(3)

        registration_field.send_keys(
            Keys.ARROW_UP)

        time.sleep(5)

        registration_field.send_keys(
            Keys.ENTER)

        # time.sleep(5)

        # self._driver.find_element(By.ID, "application_snils").click()
        # self._driver.find_element(By.ID, "application_snils").send_keys(
        #     passport.snils_number)

        time.sleep(.5)

        self._driver.find_elements(By.CSS_SELECTOR, 'div[role="combobox"]')[0].click()
        self._click_random_selector()

        time.sleep(.5)

        self._driver.find_elements(By.CSS_SELECTOR, 'div[role="combobox"]')[1].click()
        self._click_random_selector()

        time.sleep(.5)

        self._driver.find_elements(By.CSS_SELECTOR, 'div[role="combobox"]')[2].click()
        self._click_selector(number=random.randint(1, 3))

        self._driver.find_elements(By.CSS_SELECTOR, ".new-ui-button.-primary")[0].click()

        time.sleep(20)

    def enter_owner_funds_status(self):
        if "занятость и стаж" not in self._driver.page_source.lower():
            raise Exception("Credentials validation error!")

        self._select_employment_type()

        self._driver.find_elements(By.CSS_SELECTOR, ".new-ui-button.-primary")[0].click()

        try:
            WebDriverWait(self._driver, 50).until(
                expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".new-ui-button.-primary.-s")
                )
            )
        except:
            pass
        else:
            self._re_pass_all_screens()

    def _back_to_entering_phone(self, new_phone: str):
        self._driver.find_element(By.CSS_SELECTOR, ".code-form__secondary-link.secondary-link").click()

    def _select_employment_type(self):
        WebDriverWait(self._driver, 50).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, ".new-ui-select__activator.-primary.-medium")
            )
        )

        self._driver.find_elements(
            By.CSS_SELECTOR, ".new-ui-select__activator.-primary.-medium"
        )[0].click()

        random_working_strategy = 0 if random.randint(0, 100) < -10 else (
            random.randint(5, 6) if random.randint(0, 10) < 4 else 4
        )

        # random_working_strategy = random.randint(5, 6) if random.randint(0, 10) < 3 else 4

        random_working_strategy = 0

        print(f"WORK STRAT: {random_working_strategy}")

        self._click_selector(number=random_working_strategy)

        self._driver.find_elements(
            By.CSS_SELECTOR, ".new-ui-select__activator.-primary.-medium"
        )[1].click()

        print("CLICK [1]")

        self._click_selector(number=(
            random.randint(8, 15) if random.random() < .8 else random.randint(
                5, 8)) if random.random() < .9 else random.randint(15, 20))

        print("CLICK [2]")

        if random_working_strategy < 4:
            company_info_input = self._driver.find_element(
                By.ID, "application_company-info"
            )

            self._enter_text_to_field(
                field=company_info_input,
                text=random.choice(data.Companies.choises)
            )

            print("COMPANY")

            time.sleep(2)

            self._driver.find_element(
                By.CSS_SELECTOR, 'div[data-qa="job-select__option"]'
            ).click()

            print("CLICK [3]")

            time.sleep(1)

            start_working_date_field = self._driver.find_elements(
                By.CLASS_NAME, "new-ui-input-base__container"
            )[0]

            print("START WORKING DATE")

            self._enter_text_to_field(
                field=start_working_date_field,
                text=f"{random.randint(1, 12)}.{random.randint(2016, 2022)}"
            )

            time.sleep(1)

            post_title = self._driver.find_elements(
                By.CLASS_NAME, "new-ui-input-base__container"
            )[1]

            print("POST TITLE")

            self._enter_text_to_field(
                field=post_title,
                text=random.choice(data.PositionTitles.choises)
            )

            time.sleep(1.5)

            self._driver.find_elements(By.CLASS_NAME,
                                       "new-ui-dropdown-option")[1].click()

            time.sleep(1)

            print("CLICK [4]")

            work_phone = self._driver.find_elements(
                By.CLASS_NAME, "new-ui-input-base__container"
            )[1]

            self._enter_text_to_field(
                work_phone,
                f"{random.randint(900, 999)}" +
                "".join(
                    [str(random.randint(0, 10)) for _ in range(7)]
                )
            )

            print("CLICK [5]")

            employees_count = self._driver.find_element(
                By.CSS_SELECTOR,
                ".new-ui-select__activator.-primary.-medium"
            )

            employees_count.click()

            print("CLICK [6]")

            self._click_selector(number=-1)
        elif random_working_strategy == 6:
            self._driver.find_elements(
                By.CSS_SELECTOR, ".new-ui-select__activator.-primary.-medium"
            )[2].click()

            print("CLICK [7]")

            self._click_random_selector()

        inputs_group = self._driver.find_elements(By.CLASS_NAME,
                                                  "new-ui-input__wrapper")

        print("CLICK [8]")

        inputs_group[0].send_keys(
            f"{random.randint(80, 350)}0{random.randint(0, 9)}0"
        )

        print("CLICK [9]")

        inputs_group[1].send_keys(
            f"{random.randint(0, 25) * 1000}"
        )

        print("CLICK [10]")

    def _click_random_selector(self):
        selectors = self._driver.find_elements(By.CLASS_NAME,
                                               "new-ui-dropdown-option")

        selectors[random.randint(0, len(selectors) - 1)].click()

    def _click_selector(self, number: int):
        selectors = self._driver.find_elements(By.CLASS_NAME,
                                               "new-ui-dropdown-option")

        try:
            selectors[number].click()
        except Exception as e:
            print(f"ERROR CLICK SELECTOR: {e}")
            selectors[number + 1].click()

    def _enter_owner_primary_data(self):
        WebDriverWait(self._driver, 50).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "ui-input__field")
            )
        )

        name_input = self._driver.find_elements(
            By.CLASS_NAME, "ui-input__field"
        )[-2]

        passport = self._owner_credentials.get_passport_data()

        full_name = f"{passport.lastname.capitalize()} {passport.firstname.capitalize()} " + (
                    "" or passport.patronymic.capitalize())

        name_input.send_keys(full_name)

        time.sleep(2)

        self._click_first_selector()

        time.sleep(1)

        if len(passport.patronymic) < 2:
            print(self._driver.find_elements(By.NAME, "patronymic"))
            self._driver.find_element(By.NAME, "patronymic").click()

        time.sleep(1)

        email_input = self._driver.find_element(
            By.ID, "contacts-form_input-email"
        )
        email_input.send_keys(self._owner_credentials.get_email())

        time.sleep(1)

        self._driver.find_elements(
            By.CSS_SELECTOR, ".new-ui-button.-primary.-s"
        )[0].click()

    def _click_first_selector(self):
        self._driver.find_elements(By.CLASS_NAME, "ui-dropdown-option")[
            0].click()

    def _enter_password(self):
        WebDriverWait(self._driver, 15).until(
            expected_conditions.element_to_be_clickable(
                (By.ID, "simple-registration-input-new-password")
            )
        )

        password_field = self._driver.find_element(
            By.ID, "simple-registration-input-new-password"
        )

        password_field.click()

        password_field.send_keys(
            self._owner_credentials.get_random_password()
        )

        self._driver.find_element(By.ID,
                                  "simple-registration-button-set-password").click()

    def _enter_registration_otp(self, otp: int | str):
        otp = str(otp)

        WebDriverWait(self._driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.ID, "simple-registration-code-input-1")
            )
        )

        for number, otp_char in enumerate(otp, start=1):
            self._driver.find_element(By.ID,
                                      f"simple-registration-code-input-{number}").send_keys(
                otp_char
            )

            time.sleep(.25)

        WebDriverWait(self._driver, 30).until(
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

        if self._form_already_inited:
            phone_input.send_keys(Keys.CONTROL+"A")
            phone_input.send_keys(Keys.BACKSPACE)
            phone_input.send_keys(Keys.BACKSPACE)

        time.sleep(0.1)

        phone_input.send_keys(phone)

        time.sleep(0.5)

        self._driver.find_element(
            By.ID, "simple-registration-button-add-phone"
        ).click()

        self._check_number_entered(phone=phone)

    def _check_number_entered(self, phone: str):
        phone_label = self._driver.find_element(By.CSS_SELECTOR,
                                                'span[x-text="phone"]')

        for phone_symbol in phone:
            print(f"{phone_symbol} : {phone_label.text}")

            if phone_symbol not in phone_label.text:
                raise ValueError("Phone not entered")

    def _click_get_account(self):
        try:
            WebDriverWait(self._driver, 15).until(
                expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     ".AmountForm_formButton__ElYzT.finkit-button.finkit-button--primary.finkit-button--m")
                )
            )
        except:
            try:
                self._driver.execute_script(
                    "document.getElementsByClassName('TermsServicesPlate_plate__eA7cc')[0].remove()")
            except:
                raise exceptions.TraficBannedError()

        self._driver.execute_script(
            "document.getElementsByClassName('TermsServicesPlate_plate__eA7cc')[0].remove()")

        time.sleep(5)

        print("TEST")

        try:
            self._driver.find_element(
                By.CSS_SELECTOR,
                ".AmountForm_formButton__ElYzT.finkit-button.finkit-button--primary.finkit-button--m"
            ).click()
        except:
            print("FUCK")

            time.sleep(2.5)
            return self._click_get_account()

    def _select_registration_provider(self):
        try:
            WebDriverWait(self._driver, 50).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[1]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[2]/button")
                )
            )
        except:
            raise exceptions.TraficBannedError()

        self._driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div[2]/button"
        ).click()

    def _enter_text_to_field(self, field: "SeleniumWebElement", text: str):
        print("START ENTER TEXT", text)

        field.click()

        field.send_keys(text)

    def _re_pass_all_screens(self):
        WebDriverWait(self._driver, 20).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".new-ui-button.-primary.-s")
            )
        )

        self._driver.find_elements(By.CSS_SELECTOR, ".new-ui-button.-primary.-s")[0].click()

        WebDriverWait(self._driver, 50).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".new-ui-button.-primary.-s")
            )
        )

        self._driver.find_elements(By.CSS_SELECTOR, ".new-ui-button.-primary")[0].click()

        WebDriverWait(self._driver, 50).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".new-ui-button.-primary.-s")
            )
        )

        self._driver.find_elements(By.CSS_SELECTOR, ".new-ui-button.-primary")[0].click()
