from django.test import tag

from tests.assistance.backend_tests import AssistanceClassForTC
from website.management.commands.add_off_data import Command
from website.models import Product, Nutrition, Media
from website.selection_tools import replacement_picker

@tag("t2")
class TestProductSelectorModule(AssistanceClassForTC):
    
    @tag("t2-p1")
    def test_if_replacement_picker_only_accepts_int(self):
        
        print("\nTest 2 - (1/2) : replacement_picker() n'accepte-t-il que des Integers ?\n")
        
        for product in self.get_random_products(10):
            for types in [str(), bool(), list(), dict(), set(), bytes()]:
                with self.assertRaises(TypeError):
                    substitute = replacement_picker(product, types, types)

    @tag("t2-p2")
    def test_if_the_replacement_product_is_better_from_a_nutrition_standpoint(self):
        print("\nTest 2 - (2/2) : replacement_picker() offre-t-il des produits au nutriscore équivalent ou meilleur?\n")

        for product in self.get_random_products(20): 

            substitute = replacement_picker(product, 0,1)[0] 

            self.assertLessEqual(
                ord(substitute.nutrition.nutriscore), 
                ord(product.nutrition.nutriscore))
