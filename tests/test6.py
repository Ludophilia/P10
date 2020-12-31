import time, random

from django.test import tag
from django.contrib.auth.models import User

from tests.assistance.frontend_tests import AssistanceClassForSLSTC
from website.models import Record, Product

@tag("t6")
class TestSubstituteRecording(AssistanceClassForSLSTC):

    @tag("t6-p1")
    def test_if_the_user_can_save_and_unsave_a_substitute(self):
        
        print("\nTest 6 - (1/3) : La fonction d'enregistrement et de suppression produit fonctionne-t-elle ?\n")

        luser_info = self.get_or_create_luser_and_sign_up()
        luser = User.objects.get(username = luser_info['username'])

        for product in self.get_random_products(10):
            
            random_number = random.randint(0, 5)
            subsitute_name, save_link = self.replace_product_and_select_a_substitute(product.product_name, random_number)
                
            self.click_and_wait(save_link, 1)
            
            luser_entry = Record.objects.filter(user__exact=luser).first()
            self.assertEqual(luser_entry.substitute.product_name.replace("  ", " "), subsitute_name.text)

            self.click_and_wait(save_link, 1)
            self.assertEqual(Record.objects.count(), 0)

    @tag("t6-p2")
    def test_if_the_save_button_label_change_correctly_when_an_user_save_and_remove_a_product(self):
        
        print("\nTest 6 - (2/3) : Le label sur le bouton de sauvegarde change-t-il en fonction de l'action de l'utilisateur ? Son état est-il conservé après rafraichissement\n")

        self.get_or_create_luser_and_sign_up()

        for product in self.get_random_products(5):

            random_number = random.randint(0,5)

            save_link = self.replace_product_and_select_a_substitute(product.product_name, random_number)[1]

            self.assertEqual("Sauvegarder", save_link.text)
            self.click_and_wait(save_link, 1)
            self.assertEqual("Sauvegardé", save_link.text)
            self.driver.refresh()

            save_link_ag = self.select_a_substitute(random_number)[1]
            self.assertEqual("Sauvegardé", save_link_ag.text)
            self.click_and_wait(save_link_ag, 1)
            self.assertEqual("Sauvegarder", save_link_ag.text)

    @tag("t6-p3")
    def test_if_the_save_button_label_is_correctly_hidden_to_an_anonymous_user(self):
        
        print("\nTest 6 - (3/3) : Le bouton de sauvegarde est-il bien caché à l'utilisateur anonyme ?\n")

        self.driver.get(f"{self.live_server_url}/logout")

        for product in self.get_random_products(5):

            con_link = self.replace_product_and_select_a_substitute(product.product_name)[1]

            self.assertIn("Connectez-vous pour", con_link.text)
