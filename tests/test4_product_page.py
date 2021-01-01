import random, time

from django.test import tag, Client
from django.urls import reverse
from django.utils.http import urlencode

from tests.assistance.frontend_tests import AssistanceClassForSLSTC

@tag("t4")
class TestProductPage(AssistanceClassForSLSTC):

    @tag("t4-p1")
    def test_if_the_webpage_is_correctly_displayed(self):

        print("\nTest 4 - (1/3) : la page produit charge-t-elle correctement ?\n")

        self.response = Client().get(reverse("product"), {'query':'Orangina'})
        self.assertEqual(self.response.status_code, 200)

    @tag("t4-p2")
    def test_if_the_link_to_a_product_page_from_the_result_page_works_perfectly(self):

        print("\nTest 4 - (2/3) : les liens vers les pages produit depuis la page de recherche sont-ils fonctionnels ?\n")
        
        for product in self.get_random_products(10):

            selected_link = self.replace_product_and_select_a_substitute(product)[0]
            selected_product = selected_link.text
            self.click_and_wait(selected_link, 1)

            selected_link_url = f"{self.live_server_url}/product?{urlencode({'query': selected_product})}"
            self.assertEqual(self.driver.current_url.replace("%20", ""), selected_link_url.replace("+", "").replace("%2F","/"))

    @tag("t4-p3")
    def test_if_the_right_data_is_on_the_product_page(self):

        print("\nTest 4 - (3/3) : Les données nutritionnelles figurent-elles bien sur la page produit ? \n")

        labels = ["Nutriscore", "Energie", "Lipides", "dontgraissessaturées", "Sucres", "Sel"]

        for product in self.get_random_products(10):

            selected_link = self.replace_product_and_select_a_substitute(product)[0]
            self.click_and_wait(selected_link, 1)
            
            product_data = self.driver.find_element_by_css_selector("h2 + p")

            dict_product_data = {}

            for combinaison in product_data.text.split("\n"):
                combinaison_list = combinaison.split(":")
                if len(combinaison_list) > 1:
                    product_data_key = combinaison_list[0].replace(" ", "")
                    product_data_value = combinaison_list[1].replace(" ", "")
                    dict_product_data[product_data_key] = product_data_value
                    self.assertIn(product_data_key, labels)
            
            self.assertEqual(len(dict_product_data), 6)
