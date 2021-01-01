import time

from django.test import tag, Client
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from tests.assistance.frontend_tests import AssistanceClassForSLSTC

@tag("t5a")
class TestUserAccountCreation(AssistanceClassForSLSTC):

    @tag("t5a-p1")
    def test_if_user_account_data_is_correctly_added_to_the_database(self):
        
        print("\nTest 5a - (1/1) : l'ajout d'un utilisateur en BDD fonctionne-t-il sans problème ?\n")

        luser = self.get_or_create_luser_and_sign_up(True)
        user_added = User.objects.get(username="lusername")

        self.assertEqual(user_added.username, luser["username"])
        self.assertEqual(user_added.first_name, luser["first_name"])
        self.assertEqual(user_added.last_name, luser["last_name"])
        self.assertEqual(user_added.email, luser["email"])
        self.assertTrue(check_password(luser["password"], user_added.password))

@tag("t5b")
class TestUserAccountConnection(AssistanceClassForSLSTC):
    
    @tag("t5b-p1")
    def test_if_connection_works_as_expected(self):
        
        print("\nTest 5b - (1/2) : la connexion fonctionne-t-elle sans problèmes ? La redirection vers la page d'accueil se fait-elle correctement ?\n")

        self.get_or_create_luser_and_sign_up()
        self.assertEqual(self.driver.current_url, f"{self.live_server_url}/")

    @tag("t5b-p2")
    def test_if_connection_form_displays_the_error_message(self):

        print("\nTest 5b - (2/2) : le message d'erreur apparait-il bien quand l'utilisateur entre un login incorrect ?\n")

        user = dict(username = "jobsfan123", password = "johnappleseed")
        self.sign_up_user(user)

        error_message = "Saisissez un nom d'utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)."
        error_message_in_webpage = self.driver.find_element_by_css_selector("ul.errorlist li")

        self.assertEqual(error_message, error_message_in_webpage.text)

@tag("t5c")
class TestAccountPage(AssistanceClassForSLSTC):

    def setUp_and_get_luser(self, complete=False):

        luser = self.get_or_create_luser_and_sign_up(complete)
        self.driver.get(f"{self.live_server_url}/account")
        time.sleep(1)

        return luser

    @tag("t5c-p1")
    def test_if_anonymous_user_is_redirected_to_sign_in_page(self):
        
        print("\nTest 5c - (1/4) : la page 'mon compte' est-elle uniquement accessible aux utilisateurs connectés ?\n")
        
        self.client = Client()

        response = self.client.get("/account")
        self.assertRedirects(response,"/signin?next=/account")
        self.assertEqual(response.status_code, 302) 

        luser = self.get_or_create_luser()
        self.client.post("/signin", data=luser)
        response = self.client.get("/account")
        self.assertEqual(response.status_code, 200) 

    @tag("t5c-p2")
    def test_if_user_name_appear_on_account_page_header(self):

        print("\nTest 5c - (2/4) : le nom de l'utilisateur apparait-il bien dans le header ?\n")

        luser = self.setUp_and_get_luser()

        page_header = self.driver.find_element_by_css_selector("h1")
        self.assertEqual(page_header.text, f"Ahoy {luser['username']} !".upper())
    
    @tag("t5c-p3")
    def test_if_the_form_does_display_user_account_info(self):
        
        print("\nTest 5c - (3/4) : les infos de l'utilisateur figurent-elles bien dans le formulaire ?\n")

        luser = self.setUp_and_get_luser(True)
        
        for fieldname in luser:
            selector = f"[name={fieldname}]" if fieldname != "email" else f"[type=email]"
            field = self.driver.find_element_by_css_selector(selector)

            if fieldname != "password":
                self.assertEqual(field.get_attribute("value"), luser.get(fieldname))
    
    @tag("t5c-p4")
    def test_if_the_user_is_not_allowed_to_modify_his_account_info(self):

        print("\nTest 5c - (4/4) : Le formulaire est-il bien désactivé ?\n")

        luser = self.setUp_and_get_luser()

        fieldset = self.driver.find_element_by_css_selector("fieldset")
        self.assertEqual(fieldset.get_attribute("disabled"), "true")
