import os, time, random

from django.test import Client, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from website.models import Product
from website.management.commands.add_off_data import Command

@tag("autoc")
class TestAutocompleteFeature(StaticLiveServerTestCase):

    def setUp(self):
        command = Command()
        command.handle()

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

        self.driver.get("{}".format(self.live_server_url))


    def tearDown(self):
        self.driver.quit()

    # Quoi tester ?

    # Que taper un nom de produit donne bien des suggestions en lien avec le nom de ce produit

    @tag("autocft")
    def test_if_the_autocomplete_feature_work_on_homepage_search_bar(self):
        
        inputs = [
            self.driver.find_element_by_css_selector("form.input-group > input"),
            self.driver.find_element_by_css_selector("form.input-group-fake > input")
        ]

        for input in inputs:

            eqvs = [{"query": "ab", "expected": "Abricots de Méditerranée"}, 
                {"query": "or", "expected": "Orangina"},
                {"query": "nu", "expected": "Nutella"},
                {"query": "po", "expected": "Pom'Potes (Pomme)"},
                {"query": "ex", "expected": "Extrême Chocolat"},
                {"query": "q", "expected": "Quaker Oats"},
                {"query": "a", "expected": "Activia saveur citron"},
                {"query": "v", "expected": "Velouté Nature"},
                {"query": "ic", "expected": "Ice Tea Pêche"},
                {"query": "bn", "expected": "BN goût chocolat"}]
                
            for eq in eqvs:

                input.send_keys(eq["query"])

                time.sleep(2)

                suggestions = [sug.text for sug in self.driver.find_elements_by_css_selector(".ac-item")]

                self.assertIn(eq["expected"], suggestions) #regExp ?

                input.clear()

    @tag("autocftg")
    def test_if_the_autocomplete_window_appear_and_disappear_when_the_user_puts_the_focus_in_and_out_the_search_in_put(self):

        inputs = [
            self.driver.find_element_by_css_selector("form.input-group > input"),
            self.driver.find_element_by_css_selector("form.input-group-fake > input")
        ]

        for input in inputs:

            #Mettre le focus sur l'input 

            input.send_keys("ex")

            time.sleep(2)

            ac_window = self.driver.find_element_by_css_selector(".autocomplete-items") #Marche avec les deux parce qu'on commence avec le deuxième
            ac_window_cls = ac_window.get_attribute("class")

            self.assertEqual("autocomplete-items", ac_window_cls)

            #Mettre le focus ailleurs (avec un click)

            body = self.driver.find_element_by_css_selector("body")
            ActionChains(self.driver).click(body).perform()

            time.sleep(2)

            ac_window = self.driver.find_element_by_css_selector(".autocomplete-items")
            ac_window_cls = ac_window.get_attribute("class")
            
            self.assertEqual("autocomplete-items d-none", ac_window_cls)

            #Remettre le focus sur l'input

            input.send_keys("t")

            time.sleep(2)

            ac_window = self.driver.find_element_by_css_selector(".autocomplete-items")

            ac_window_cls = ac_window.get_attribute("class")
            
            self.assertEqual("autocomplete-items", ac_window_cls)

            #Retirer le contenu de l'input
            
            for _ in range(3):
                input.send_keys(Keys.BACKSPACE)

            time.sleep(2)

            ac_window = self.driver.find_element_by_css_selector(".autocomplete-items")

            ac_window_cls = ac_window.get_attribute("class")
            
            self.assertEqual("autocomplete-items d-none", ac_window_cls)

            #Remettre du contenu

            input.send_keys("or")

            time.sleep(2)

            ac_window = self.driver.find_element_by_css_selector(".autocomplete-items")

            ac_window_cls = ac_window.get_attribute("class")
            
            self.assertEqual("autocomplete-items", ac_window_cls)

    @tag("autocftt")
    def test_if_clicking_on_one_the_autocomplete_suggestion_lead_the_user_to_the_product(self):
        
        count = 0

        eqvs = [{"query": "Abricots de M", "expected": "Abricots de Méditerranée"}, 
                {"query": "orangi", "expected": "Orangina"},
                {"query": "nutel", "expected": "Nutella"},
                {"query": "Pom'Potes (", "expected": "Pom'Potes (Pomme)"},
                {"query": "Extrême Ch", "expected": "Extrême Chocolat"},
                {"query": "quak", "expected": "Quaker Oats"},
                {"query": "activia n", "expected": "Activia Nature"},
                {"query": "velouté n", "expected": "Velouté Nature"},
                {"query": "ice te", "expected": "Ice Tea Pêche"},
                {"query": "bn", "expected": "BN goût chocolat"}]

        for eq in eqvs:

            for _ in range(2):

                if count == 0:
                    input = self.driver.find_element_by_css_selector("form.input-group > input")
                else:
                    input = self.driver.find_element_by_css_selector("form.input-group-fake > input")

                for character in eq["query"]: 
                    input.send_keys(character)
                    time.sleep(0.1)

                time.sleep(1)

                first_result = self.driver.find_element_by_css_selector(".ac-item:first-child")
                ActionChains(self.driver).click(first_result).perform()

                time.sleep(2)

                producthd = self.driver.find_element_by_css_selector("h1")
                self.assertIn(eq["expected"].upper(), producthd.text)
                self.assertIn("/search?query=", self.driver.current_url)

                count+=1

                if count >= 1:
                    
                    self.driver.get("{}".format(self.live_server_url))
                    time.sleep(2)

                    if count > 1:
                        count = 0



