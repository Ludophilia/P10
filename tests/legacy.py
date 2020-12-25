import os, time, random, requests
from decimal import Decimal

from django.test import TestCase, Client, tag, SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from website.models import Product, Nutrition, Media, Record
from website.management.commands.add_off_data import Command
from website.selection_tools import replacement_picker
from website.views import results

# A quick n dirty way to make this sh* compatible with travis-ci
options = webdriver.ChromeOptions()

# And now the tests.





@tag("account")
class TestUserAccountCreation(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))
   
    def tearDown(self):
        self.driver.quit() 

    def test_if_user_account_data_is_correctly_added_to_the_database(self):
        
        user_info = {
                "username":"lusername",
                "last_name":"last",
                "first_name":"first",
                "mail":"first_last_who_cares@me.com",
                "password":"mucho_secure"
            }

        self.driver.get("{}{}".format(self.live_server_url, '/signup'))

        for field in ["username", "first_name", "last_name", "mail", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)
        
        user_added = User.objects.get(username="lusername")

        self.assertEqual(user_added.username, user_info["username"])
        self.assertEqual(user_added.first_name, user_info["first_name"])
        self.assertEqual(user_added.last_name, user_info["last_name"])
        self.assertEqual(user_added.email, user_info["mail"])
        self.assertTrue(check_password(user_info["password"], user_added.password))

@tag("connect")
class TestUserAccountConnection(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))
    
    def tearDown(self):
        self.driver.quit() 

    def test_if_connection_form_displays_the_error_message(self):

        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        self.driver.get("{}/{}".format(self.live_server_url, "signin"))
        time.sleep(3)

        for field in ["username", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)

        error_message = "Saisissez un nom d'utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)."

        error_message_in_webpage = self.driver.find_element_by_css_selector("ul.errorlist li")

        self.assertEqual(error_message, error_message_in_webpage.text)
    
    @tag("works")
    def test_if_connection_works_as_expected(self):
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        self.driver.get("{}/{}".format(self.live_server_url, "signin"))
        time.sleep(1)

        for field in ["username", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)

        self.assertEqual(self.driver.current_url, self.live_server_url+"/")

@tag("connectDjango")
class TestUserAccountConnectionDjangoClientVersion(TestCase):
    
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass
    
    @tag("error2")
    def test_if_connection_form_displays_the_error_message(self):

        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        response = self.client.post(path=reverse("signin"), data=user_info)

        error_message = "Saisissez un nom d&#39;utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)." #Eeeet oui, on réplique les erreurs

        self.assertIn(error_message, response.content.decode())

    @tag("works2")
    def test_if_connection_works_as_expected(self):
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        response = self.client.post(path=reverse("signin"), data=user_info)

        error_message = "Saisissez un nom d&#39;utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)."

        self.assertNotIn(error_message, response.content.decode())

        self.assertEqual(response.url, "/") # Juste la partie après le nom de domaine


class TestAccountPage(StaticLiveServerTestCase):

    def setUp(self):
        
        self.user_info = {
            "username" : "lusername",
            "password" : "mucho_secure",
            "mail": "lusername@makeinu.com",
            "first_name": "luser",
            "last_name": "dunner"
        }

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))
        
        User.objects.create_user (
            username = self.user_info['username'],
            password = self.user_info['password'],
            email = self.user_info['mail'],
            first_name = self.user_info['first_name'],
            last_name = self.user_info['last_name']
        )

        self.driver.get('{}{}'.format(self.live_server_url, '/signin'))

        for fieldname in ['username', "password"]:
            field = self.driver.find_element_by_name(fieldname)
            field.send_keys(self.user_info[fieldname])

            if fieldname == "password":
                field.submit()
        
        self.driver.get('{}{}'.format(self.live_server_url, '/account'))

        time.sleep(1)

    def tearDown(self):
        self.driver.quit()

    @tag("myusername")
    def test_if_user_name_appear_on_account_page_header(self):
        
        # Tester que le nom de l'utilisateur apparait bien dans le header

        element = self.driver.find_element_by_css_selector("h1")
        self.assertEqual(element.text, "Ahoy {} !".format(self.user_info['username']).upper())
    
    @tag("accountinfo")
    def test_if_the_form_does_display_user_account_info(self):
        
        # Tester que le formulaire affiche bien les informations de l'utilisateur

        for fieldname in self.user_info:
            field = self.driver.find_element_by_name(fieldname)
            if fieldname != "password":
                self.assertEqual(field.get_attribute("value"), self.user_info[fieldname])
    
    @tag("userdont")
    def test_if_the_user_is_not_allowed_to_modify_his_account_info(self):

        # Tester que le formulaire n'est pas modifiable par l'utilisateur

        fieldset = self.driver.find_element_by_css_selector("fieldset")
        self.assertEqual(fieldset.get_attribute("disabled"), "true")

class TestSubstituteRecording(StaticLiveServerTestCase):

    def setUp(self):
        
        # Remplissage de la base en produits

        self.command = Command()
        self.command.handle()
        
        # Création d'un utilisateur

        self.user_info = {
            "username" : "lusername",
            "password" : "mucho_secure",
            "mail": "lusername@makeinu.com",
            "first_name": "luser",
            "last_name": "dunner"
        }

        User.objects.create_user (
            username = self.user_info['username'],
            password = self.user_info['password'],
            email = self.user_info['mail'],
            first_name = self.user_info['first_name'],
            last_name = self.user_info['last_name']
        )

        # Connexion utiilisateur

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

        self.driver.get('{}{}'.format(self.live_server_url, '/signin'))

        for fieldname in ['username', "password"]:
            field = self.driver.find_element_by_name(fieldname)
            field.send_keys(self.user_info[fieldname])

            if fieldname == "password":
                field.submit()
        
    def tearDown(self):
        self.driver.quit()
    
    @tag("srecord")
    def test_if_the_user_can_save_and_unsave_a_substitute(self):
        
        # Obtenir la page produit, celle d'orangina typiquement

        # self.driver.get('{}{}'.format(self.live_server_url, '/'))

        # searchbox = self.driver.find_element_by_name("query")
        # searchbox.send_keys("orangina")
        # searchbox.submit()

        self.driver.get('{}{}'.format(self.live_server_url, '/search?query=orangina'))

        save_link = self.driver.find_elements_by_css_selector("a.save-link")[0]

        ActionChains(self.driver).click(save_link).perform()

        time.sleep(1)
        
        # print(Record.objects.all())

        recording = Record.objects.get(pk=1)
        subsitute = self.driver.find_elements_by_css_selector("h3.results")[0].text

        self.assertEqual(recording.user.username, "lusername")
        self.assertEqual(recording.substitute.product_name, subsitute)

        # Recliquer sur le même lien et voir si le produit disparait de la table.

        ActionChains(self.driver).click(save_link).perform()

        time.sleep(1)

        user_obj = User.objects.filter(username__exact="lusername")[0]
        user_products = Record.objects.filter(user__exact=user_obj) #Qu'un seul produit ajouté donc nécessairement
        
        # print("nombre:", user_products.count())

        self.assertLessEqual(user_products.count(), 1)

    @tag("sbuttons")
    def test_if_the_save_button_label_change_correctly_when_an_user_save_and_remove_a_product(self):
        
        self.driver.get('{}{}'.format(self.live_server_url, '/search?query=orangina'))

        # On vérifie si le bouton marque "Sauvegarder" si on est connecté

        second_save_link = self.driver.find_element_by_name("Eau de source gazéifiée").find_element_by_class_name("save-link")
        self.assertEqual("Sauvegarder", second_save_link.text)

        # # On vérifie si le bouton marque "Sauvegardé" si on appuie sur le bouton

        ActionChains(self.driver).click(second_save_link).perform()
        time.sleep(1) #Important, pour laisser tous les changements se faire...
        self.assertEqual("Sauvegardé", second_save_link.text)

        # On vérifie si le bouton marque toujours "Sauvegardé" si on rafraichit la page

        self.driver.refresh()

        second_save_link_ag = self.driver.find_element_by_name("Eau de source gazéifiée").find_element_by_class_name("save-link")
        self.assertEqual("Sauvegardé", second_save_link_ag.text)

        #On vérifie si appuyer sur le bouton faire passer le message à "Sauvegarder"

        ActionChains(self.driver).click(second_save_link_ag).perform()
        time.sleep(1)
        self.assertEqual("Sauvegarder", second_save_link_ag.text)

    @tag("anon-sbuttons")
    def test_if_the_save_button_label_is_correctly_hidden_to_an_anonymous_user(self):
        
        # On se déco et récupère la page 

        self.driver.get('{}{}'.format(self.live_server_url, '/logout')) #PAs moyen de ne pas lancer setup?
        self.driver.get('{}{}'.format(self.live_server_url, '/search?query=orangina'))

        # On vérifie si les boutons marquent bien "Connectez-vous pour" quand l'utilisateur n'est pas connecté

        second_save_link = self.driver.find_element_by_name("Eau de source gazéifiée").find_element_by_class_name("con-link")

        # print(second_save_link, second_save_link.text)
        self.assertIn("Connectez-vous pour", second_save_link.text)

@tag("my")
class TestMyProductPage(StaticLiveServerTestCase):
    
    def setUp(self):

        # Remplissage de la base en produits

        self.command = Command()
        self.command.handle()
        
        # Création d'un utilisateur

        self.user_info = {
            "username" : "lusername",
            "password" : "mucho_secure",
            "mail": "lusername@makeinu.com",
            "first_name": "luser",
            "last_name": "dunner"
        }

        User.objects.create_user (
            username = self.user_info['username'],
            password = self.user_info['password'],
            email = self.user_info['mail'],
            first_name = self.user_info['first_name'],
            last_name = self.user_info['last_name']
        )

        # Connexion utiilisateur

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

        self.driver.get('{}{}'.format(self.live_server_url, '/signin'))

        for fieldname in ['username', "password"]:
            field = self.driver.find_element_by_name(fieldname)
            field.send_keys(self.user_info[fieldname])

            if fieldname == "password":
                field.submit()

    def tearDown(self):
        self.driver.quit()

    def test_if_the_page_displays_correctly(self):
        
        base_url = self.live_server_url
        self.driver.get('{}{}'.format(base_url, '/myproducts'))
        self.assertEqual(self.driver.current_url, '{}{}'.format(base_url, '/myproducts'))

    @tag('my-lr')
    def test_if_the_page_displays_only_to_logged_users(self):
        
        base_url = self.live_server_url

        self.driver.get('{}{}'.format(base_url, '/logout'))
        self.driver.get('{}{}'.format(base_url, '/myproducts'))
        self.assertNotEqual(self.driver.current_url, '{}{}'.format(base_url, '/myproducts'))

    @tag('my-pg')
    def test_if_the_products_saved_by_the_user_are_displayed_correctly(self):

        products = ["bâtonnets de surimi", "Filets de Colin Panés", "Salade de quinoa aux légumes", "Les bios vanille douce sava", "Coquillettes", "Salade & Compagnie - Montmartre"]
        user = User.objects.get(username="lusername")

        for product in products:
            # print("product:", Product.objects.get(product_name=product))
            Record.objects.create(
                user = user,
                substitute = Product.objects.get(product_name=product)
            )

        print("records au total:", Record.objects.count())

        time.sleep(1)

        base_url = self.live_server_url

        self.driver.get('{}{}'.format(base_url, '/myproducts'))

        for h3_block in self.driver.find_elements_by_css_selector("h3"):
            print("Dans cet h3:", h3_block.text)
            self.assertIn(h3_block.text, products)

    @tag('my-rm')
    def test_if_clicking_on_the_save_button_on_the_page_still_remove_the_product(self):
        
        products = ["bâtonnets de surimi", "Filets de Colin Panés", "Salade de quinoa aux légumes", "Les bios vanille douce sava", "Coquillettes", "Salade & Compagnie - Montmartre"]
        user = User.objects.get(username="lusername")

        for product in products:
            Record.objects.create(
                user = user,
                substitute = Product.objects.get(product_name=product)
            )

        number_of_products = Record.objects.count()
        print("records au total:", number_of_products)

        time.sleep(1)

        base_url = self.live_server_url
        self.driver.get('{}{}'.format(base_url, '/myproducts'))

        save_links = self.driver.find_elements_by_css_selector("a.save-link")

        for link in save_links:
            ActionChains(self.driver).click(link).perform()
        
        time.sleep(3)

        self.assertEqual(Record.objects.count(), 0)

@tag("prodwork")
class TestProductPageDjC(TestCase):
    
    def setUp(self):
        command = Command()
        command.handle()
        
    def test_if_the_webpage_is_correctly_displayed(self):

        self.client = Client()
        self.response = self.client.get(reverse("product"), {'query':'Orangina'})
        self.assertEqual(self.response.status_code, 200)

@tag("product")
class TestProductPage(StaticLiveServerTestCase):

    def setUp(self):
        command = Command()
        command.handle()

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

    def tearDown(self):
        self.driver.quit()

    @tag("prodred")
    def test_if_the_link_to_a_product_page_from_the_result_page_works_perfectly(self):
        
        #On est en mode anonyme, je précise bien que ça ne change pas grand chose

        product_list = ["orangina", "nutella", "salade de quinoa aux légumes"] #On peut en mettre plus
        product = product_list[random.randint(0, len(product_list)-1)]

        self.driver.get("{}{}".format(self.live_server_url, "/search?query={}".format(product)))

        product_links = self.driver.find_elements_by_css_selector("h3 > a")

        product_index = random.randint(0,len(product_links)-1)
        selected_link = product_links[product_index]

        selected_link_url = product_url_builder(selected_link.text)
        absolute_selected_link_url = "{}{}".format(self.live_server_url, selected_link_url)
        
        ActionChains(self.driver).click(selected_link).perform()
        time.sleep(2)

        self.assertEqual(self.driver.current_url, absolute_selected_link_url)

        #Si cliquer sur n'importe quel lien lien dans la page de résultat renvoie vers la page produit

    @tag("prodat")
    def test_if_the_right_data_is_on_the_product_page(self):

        product_list = ["orangina", "nutella", "salade de quinoa aux légumes"] #On peut en mettre plus
        product_selected = product_list[random.randint(0, len(product_list)-1)]

        self.driver.get("{}{}".format(self.live_server_url, "/search?query={}".format(product_selected)))

        substitutes_links = self.driver.find_elements_by_css_selector("h3 > a")
        selected_link = substitutes_links[random.randint(0,len(substitutes_links)-1)]
        ActionChains(self.driver).click(selected_link).perform()

        time.sleep(1)
        
        product_data = self.driver.find_element_by_css_selector("h2 + p")
        nutriscore = self.driver.find_elements_by_css_selector("img[src*='images/misc/nutriscore']")
        dict_product_data = {}

        for combinaison in product_data.text.split("\n"):
            combinaison_list = combinaison.split(":")
            if len(combinaison_list) > 1:
                product_data_key = combinaison_list[0].replace(" ", "")
                product_data_value = combinaison_list[1].replace(" ", "")
                dict_product_data[product_data_key] = product_data_value
        
        self.assertEqual(len(dict_product_data), 5) #S'il y a 5 couples clé valeur, c'est que les données nutritionelles ont bien été transmises au template, indépendamment de leur qualité
        self.assertEqual(len(nutriscore), 1) #On vérifie la présence de l'image représentant le nutriscore

@tag("legwork")
class TestLegalPageDjC(StaticLiveServerTestCase):
    
    def test_if_the_webpage_is_correctly_displayed(self):

        self.client = Client()
        self.response = self.client.get(reverse("legal"))
        self.assertEqual(self.response.status_code, 200) 

@tag("isitlegal")
class TestLegalPage(StaticLiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

    def tearDown(self):
        self.driver.quit()

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



