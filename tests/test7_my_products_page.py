import time 

from django.test import tag, Client
from django.contrib.auth.models import User

from tests.assistance.frontend_tests import AssistanceClassForSLSTC
from website.models import Record, Product

@tag("t7")
class TestMyProductPage(AssistanceClassForSLSTC):
    
    @tag("t7-p1")
    def test_if_the_page_displays_correctly_only_to_logged_users(self):
        
        print("\nTest 7 - (1/3) : La page 'Mes produits' ne s'affiche-t-elle qu'aux utilisateurs authentitifiées ?\n")

        self.client = Client()
        luser = self.get_or_create_luser()
        self.client.post("/signin", data=luser)

        response = self.client.get("/myproducts")
        self.assertEqual(response.status_code, 200)

        self.client.get("/logout")

        response = self.client.get("/myproducts")
        self.assertNotEqual(response.status_code, 200)

    @tag("t7-p2")
    def test_if_the_products_saved_by_the_user_are_displayed_correctly(self):

        print("\nTest 7 - (2/3) : Les produits enregistrés par l'utilisateur s'affichent-ils bien sur la page 'Mes Produits' ?\n")

        products = self.authenticate_luser_and_save_some_products(10, True)
        self.driver.get(f"{self.live_server_url}/myproducts")

        for h3_block in self.driver.find_elements_by_css_selector("h3"):
            self.assertIn(h3_block.text, products)

    @tag("t7-p3")
    def test_if_clicking_on_the_save_button_on_the_page_still_remove_the_product(self):
        
        print("\nTest 7 - (3/3) : Le bouton de sauvegarde sur la page 'Mes Produits' fonctionne-t-il ?\n")

        products = self.authenticate_luser_and_save_some_products(8, True)

        self.driver.get(f"{self.live_server_url}/myproducts")

        save_links = self.driver.find_elements_by_css_selector("a.save-link")

        even_cycle = True
        
        for link in save_links:
            cycle = 2 if even_cycle else 1
            for _ in range(cycle):
                self.click_and_wait(link, 1)
            even_cycle = not even_cycle

        self.assertEqual(Record.objects.count(), 4)