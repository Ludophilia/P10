import os, time

from django.test import tag, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.contrib.auth.models import User
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from tests.chromedrivermgr import ChromeDriverMgr
from website.models import Product, Nutrition, Media
from website.management.commands.add_off_data import Command

class AssistanceClass:

    def setUp(self):
        call_command("loaddata", "website/dumps/website.json") #Command().handle() #Calls OFF API everytime, which is a bit expensive tbh
        self.driver = ChromeDriverMgr.get_chromedriver("mac", "87.0.4280.88")
        self.driver.get(f"{self.live_server_url}") 

    def tearDown(self):
        self.driver.quit()
    
    def create_luser_and_sign_up(self):
        self.driver.get(f"{self.live_server_url}/signin")

        self.user = dict(username = "lusername", password = "mucho_secure")

        User.objects.create_user(username = self.user['username'], password = self.user['password'])

        for type_field in self.user: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(self.user[type_field])

            if type_field == "password":
                field.submit()

@tag("t3a")
class TestProductReplacementFunction(AssistanceClass,StaticLiveServerTestCase):

    @tag("t3a-p1")
    def test_if_the_product_replacement_is_working_correctly(self):
        print("\n1/2 - Test 3a : la fonctionnalité de remplacement de produit via le formulaire fonctionne-t-elle ?\n")

        products = ["bâtonnets de surimi", "Orangina", "Perrier fines bulles", "Pâtes Spaghetti au blé complet", "Filets de Colin Panés", "Coquillettes", "Betteraves à la Moutarde à l'Ancienne"]
        
        for product in products:

            searchbox = self.driver.find_elements_by_css_selector("input.form-control")[1]
            searchbox.send_keys(product)
            searchbox.submit()

            time.sleep(2)

            substitute_name = self.driver.find_element_by_css_selector(".results.card-title").text

            product_nutriscore = Product.objects.get(product_name__iexact=product).nutrition.nutriscore
            substitute_nutriscore = Product.objects.get(product_name__iexact=substitute_name).nutrition.nutriscore     

            self.assertLessEqual(ord(substitute_nutriscore), ord(product_nutriscore))

            self.driver.get(f"{self.live_server_url}") 

    @tag("t3a-p2")
    def test_if_404_is_correctly_raised(self):
        
        print("\n2/2 - Test 3a : l'utilisateur est-il bien redirigé vers une page d'erreur en cas de requête invalide ?\n")

        searchbox = self.driver.find_element_by_name("query")
        searchbox.send_keys("orangin")
        searchbox.submit()
        time.sleep(1)

        error = self.driver.find_element_by_css_selector("h1").text
        self.assertEqual(error,"Not Found") #En mode débug s'entend

@tag("t3b")
class TestNavBarBehavior(AssistanceClass,StaticLiveServerTestCase):

    @tag("t3b-p1")
    def test_if_se_connecter_appear_in_menubar_when_the_user_is_not_connected(self):

        print("\nTest 3b - (1/3) : Le bouton 'se connecter' apparait-il quand l'utilisateur n'est pas connecté ?\n")

        connect_logo = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(connect_logo.text, "Se connecter")

    @tag("t3b-p2")
    def test_if_mon_compte_appear_in_menubar_when_the_user_is_connected(self):

        print("\nTest 3b - (2/3) : Le bouton 'mon compte' apparait-il quand l'utilisateur est connecté ?\n")

        self.create_luser_and_sign_up()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(mon_compte.text, "Mon compte")

    @tag("t3b-p3")
    def test_if_clicking_on_logout_button_does_logout_the_user(self):

        print("\nTest 3b - (3/3) : Appuyer sur le bouton de déco déconnecte-t-il l'utilisateur ?\n")

        self.create_luser_and_sign_up()

        time.sleep(3)

        logout = self.driver.find_element_by_css_selector(".fas.fa-sign-out-alt")
        ActionChains(self.driver).move_to_element(logout).click().perform()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(mon_compte.text, "Se connecter")
