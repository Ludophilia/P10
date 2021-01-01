import os, time

from django.test import tag

from tests.assistance.frontend_tests import AssistanceClassForSLSTC
from website.models import Product

@tag("t3a")
class TestProductReplacementFunction(AssistanceClassForSLSTC):

    def setUp(self):
        super().setUp()
        self.driver.get(f"{self.live_server_url}") 

    @tag("t3a-p1")
    def test_if_the_product_replacement_is_working_correctly(self):
        
        print("\nTest 3a - (1/2) : la fonctionnalité de remplacement de produit via le formulaire fonctionne-t-elle ?\n")
        
        for product in self.get_random_products(10):

            product = product.product_name
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
        
        print("\nTest 3a - (2/2) : l'utilisateur est-il bien redirigé vers une page d'erreur en cas de requête invalide ?\n")

        searchbox = self.driver.find_element_by_name("query")
        searchbox.send_keys("orangin")
        searchbox.submit()
        time.sleep(1)

        error = self.driver.find_element_by_css_selector("h1").text
        self.assertEqual(error,"Not Found") #En mode débug s'entend

@tag("t3b")
class TestNavBarBehaviorWhenNotConnected(AssistanceClassForSLSTC):

    def setUp(self):
        super().setUp()
        self.driver.get(f"{self.live_server_url}") 

    @tag("t3b-p1")
    def test_if_se_connecter_appear_in_menubar_when_the_user_is_not_connected(self):

        print("\nTest 3b - (1/1) : Le bouton 'se connecter' apparait-il quand l'utilisateur n'est pas connecté ?\n")

        connect_logo = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(connect_logo.text, "Se connecter")

@tag("t3c")
class TestNavBarBehaviorWhenConnected(AssistanceClassForSLSTC):

    def setUp(self):
        super().setUp()
        self.get_or_create_luser_and_sign_up()

    @tag("t3c-p1")
    def test_if_mon_compte_appear_in_menubar_when_the_user_is_connected(self):

        print("\nTest 3c - (1/2) : Le bouton 'mon compte' apparait-il quand l'utilisateur est connecté ?\n")

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(mon_compte.text, "Mon compte")

    @tag("t3c-p2")
    def test_if_clicking_on_logout_button_does_logout_the_user(self):

        print("\nTest 3c - (2/2) : Appuyer sur le bouton de déco déconnecte-t-il l'utilisateur ?\n")

        logout = self.driver.find_element_by_css_selector(".fas.fa-sign-out-alt")
        logout.click()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(mon_compte.text, "Se connecter")
