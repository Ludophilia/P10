import os, zipfile

import wget
from selenium import webdriver
from django.contrib.auth.models import User
from django.core.management import call_command
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 

class ChromeDriverMgr:

    @staticmethod
    def get_chromedriver(os_name: str, version: str) -> webdriver:

        """ Automatise le téléchargement du chromedriver et le renvoie pour utilisation """
        
        dirname = os.path.dirname(os.path.abspath(__file__))
        build_path = lambda filename: os.path.join(dirname, filename)

        if not os.path.exists(build_path("chromedriver")):
            
            ext = {"mac": "mac64", "win": "win32", "tux": "linux64"}.get(os_name)
            chromedriver_url = f"http://chromedriver.storage.googleapis.com/{version}/chromedriver_{ext}.zip"

            wget.download(chromedriver_url, build_path("chromedriver.zip"))

            with zipfile.ZipFile(build_path("chromedriver.zip"), mode="r") as z:
                chromedriver = z.getinfo("chromedriver")
                z.extract(chromedriver, path=build_path(""))
            
            os.system(f"chmod 755 {build_path('chromedriver')}")
            os.remove(build_path("chromedriver.zip"))

        return webdriver.Chrome(build_path('chromedriver'))

class BaseClassForSLSTC(StaticLiveServerTestCase):

    def setUp(self):
        call_command("loaddata", "website/dumps/website.json")

        ext = ("tux", "87.0.4280.88") if os.environ.get("TEST_ENV") == "TRAVIS_CI" else ("mac", "87.0.4280.88")
        self.driver = ChromeDriverMgr.get_chromedriver(*ext)

    def tearDown(self):
        self.driver.quit()

    def get_or_create_luser(self, complete=False):
        
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

    def sign_up(self, user):

        self.driver.get(f"{self.live_server_url}/signin")

        for type_field in ["username", "password"]: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user[type_field])

            if type_field == "password":
                field.submit()

    def get_or_create_luser_and_sign_up(self, complete=False):

        luser = self.get_or_create_luser(complete)
        self.sign_up(luser)

        return luser