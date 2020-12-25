import os

from django.test import tag 
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from selenium import webdriver

from tests.chromedrivermgr import ChromeDriverMgr
from website.management.commands.add_off_data import Command

@tag("t3")
class TestProductReplacementFunction(StaticLiveServerTestCase):
    
    def setUp(self):
        Command().handle()
        self.driver = ChromeDriverMgr.get_chromedriver("mac", "84.0.4147.30")

    def tearDown(self):
        self.driver.quit() 

    @tag("t3-p1")
    def test_if_the_product_replacement_is_working_correctly(self):

        products = ["bâtonnets de surimi", "Orangina", "Perrier fines bulles", "Pâtes Spaghetti au blé complet", "Salade de quinoa aux légumes", "Magnum Double Caramel"]
        
        substitutes = ["Filets de Colin Panés", "Cristaline", "Cristaline", "Coquillettes", "Betteraves à la Moutarde à l'Ancienne", "Les bios vanille douce sava"]
        i = 0
        
        for product in products:
            pass
            self.driver.get(f"{self.live_server_url}") 

            searchbox = self.driver.find_element_by_name("query")
            searchbox.send_keys(product)
            searchbox.submit()

            time.sleep(2)

            substitute_name = self.driver.find_element_by_css_selector(".results.card-title").text
            # self.assertEqual(substitute_name, substitutes[i]) # Retiré, le nom des substituts a changé en 1 mois et demi... Diable. Seul le nutriscore sera testé

            product_nutriscore = Product.objects.get(product_name__iexact=product).nutrition.nutriscore
            substitute_nutriscore = Product.objects.get(product_name__iexact=substitute_name).nutrition.nutriscore     

            self.assertLessEqual(ord(substitute_nutriscore), ord(product_nutriscore))
            i+=1
        
    @tag("repl_404")
    def test_if_404_is_correctly_raised(self):
        
        self.driver.get("{}".format(self.live_server_url)) 

        searchbox = self.driver.find_element_by_name("query")
        searchbox.send_keys("orangin")
        searchbox.submit()
        time.sleep(1)

        error = self.driver.find_element_by_css_selector("h1").text
        self.assertEqual(error,"Not Found") #En mode débug s'entend

@tag("nav")
class TestNavBarBehaviour(StaticLiveServerTestCase):    
    
    @tag("se-connecter")
    def test_if_se_connecter_appear_in_menubar_when_the_user_is_not_connected(self):
        # Tester que qu'il y ait bien marquer se connecter dans le logo de connection

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))

        self.driver.get(self.live_server_url)
        connect_logo = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(connect_logo.text, "Se connecter")

        self.driver.quit()

    @tag("nav-redirect")
    def test_if_anonymous_user_is_redirected_to_sign_in_page(self):
        # Tester que appuyer sur mon compte envoie la page de connexion en mode Anonymous user

        self.client = Client()

        response = self.client.get("/account")
        self.assertRedirects(response,"/signin?next=/account")

    @tag("mon-compte")
    def test_if_mon_compte_appear_in_menubar_when_the_user_is_connected(self):
        # Tester que qu'il y ait bien marquer se connecter dans le logo de connection une fois connecté
        self.selenium_is_active = True
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedriver"))
        self.driver.get("{}{}".format(self.live_server_url, "/signin"))
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        for type_field in user_info: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user_info[type_field])

            if type_field == "password":
                field.submit()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")

        self.assertEqual(mon_compte.text, "Mon compte")
        self.driver.quit()

    @tag("access")
    def test_if_a_connected_user_can_access_to_mon_compte_page(self):

        # Tester qu'un utilisateur connecté peut accéder au compte

        self.client = Client()

        user_info = {
            "username" : "username",
            "password" : "password"
        }

        User.objects.create_user(
            username = user_info["username"],
            password = user_info["password"]
        )

        self.client.post("/signin", data=user_info)
        response = self.client.get("/account")

        self.assertEqual(response.status_code, 200) #Si 200, c'est qu'on a pu accéder, si c'est  c'est 302 c'est qu'il y a eu une redirection

    @tag("deco")
    def test_if_clicking_on_logout_button_does_logout_the_user(self):
        
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))

        self.driver.get("{}{}".format(self.live_server_url, "/signin"))
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        for type_field in user_info: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user_info[type_field])

            if type_field == "password":
                field.submit()

        time.sleep(3)

        self.actions = ActionChains(self.driver)

        logout = self.driver.find_element_by_css_selector(".fas.fa-sign-out-alt")

        self.actions.move_to_element(logout).click().perform()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")

        self.assertEqual(mon_compte.text, "Se connecter")
        self.driver.quit()
        