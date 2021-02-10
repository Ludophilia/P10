import os, random, time

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.utils.http import urlencode
from selenium.webdriver.remote.webelement import WebElement

from website.models import Product, Record
from tests.assistance.chromedrivermgr import ChromeDriverMgr
from tests.assistance.backend_tests import AssistanceClassForTC

class AssistanceClassForSLSTC(StaticLiveServerTestCase):

    def setUp(self) -> None:

        AssistanceClassForTC().setUp()

        self.driver = ChromeDriverMgr.get_chromedriver(*("tux", "87.0.4280.88") if os.environ.get("TEST_ENV") == "TRAVIS_CI" else ("mac", "87.0.4280.88"))

        self.f, self.ff = self.driver.find_element_by_css_selector, self.driver.find_elements_by_css_selector

    def tearDown(self) -> None:

        self.driver.quit()

    def get_or_create_luser(self, complete=False) -> dict:
        
        base_luser = dict(
            username = "lusername", 
            password = "123456",
        )

        extra_luser = dict(
            last_name = "Makegumi",
            first_name = "Taro",
            email = "lusername@makeinu.co.jp"
        )

        luser = {**base_luser , **extra_luser}

        if not User.objects.filter(username__exact = "lusername"):
            User.objects.create_user(
                username = luser['username'],
                password = luser['password'],
                last_name = luser['last_name'],
                first_name = luser['first_name'],
                email = luser['email']
            )
        
        return base_luser if not complete else luser
              
    def sign_up_user(self, user: dict) -> None:

        self.driver.get(f"{self.live_server_url}/signin")

        for type_field in ["username", "password"]: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user[type_field])

            if type_field == "password":
                field.submit()

    def get_or_create_luser_and_sign_up(self, complete=False) -> dict:

        luser = self.get_or_create_luser(complete)
        self.sign_up_user(luser)
        time.sleep(1)

        return luser

    def get_random_products(self, amount: int, text_only: bool = False) -> list:

        return AssistanceClassForTC().get_random_products(amount, text_only)
    
    def select_a_substitute(self, index: int = -1) -> (WebElement, WebElement):

        title_links = self.driver.find_elements_by_css_selector("h3 > a")
        save_links = self.driver.find_elements_by_css_selector(".save-link") or \
            self.driver.find_elements_by_css_selector(".con-link")

        if index == -1 : index = random.randint(0, len(title_links)-1)

        return title_links[index], save_links[index]

    def replace_product_and_select_a_substitute(self, product: str, substitute_index = -1) -> (WebElement, WebElement):

        self.driver.get(f"{self.live_server_url}/search?{urlencode(dict(query = product))}")

        time.sleep(1)
        
        title_link, save_link = self.select_a_substitute(substitute_index)

        return title_link, save_link
    
    def click_and_wait(self, webelement: WebElement, timeout: int) -> None:

        webelement.click()
        time.sleep(timeout)
    
    def authenticate_luser_and_save_some_products(self, amount: int, text_only: bool = False) -> list:

        self.get_or_create_luser_and_sign_up()

        products = self.get_random_products(amount, text_only=text_only)

        for product in products:
            Record.objects.create(
                user = User.objects.get(username="lusername"),  
                substitute = Product.objects.get(product_name=product))
        
        return products