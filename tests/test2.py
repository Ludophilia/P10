import random

from django.test import TestCase, tag 
from django.core.management import call_command

from website.management.commands.add_off_data import Command
from website.models import Product, Nutrition, Media
from website.selection_tools import replacement_picker

@tag("t2")
class TestProductSelectorModule(TestCase):
    
    def setUp(self):
        call_command("loaddata", "website/dumps/website.json") #Command().handle() #Calls OFF API everytime, which is a bit expensive tbh.

    @tag("t2-p1")
    def test_if_replacement_picker_only_accepts_int(self):
        
        print("\nTest 2 - (1/2) : replacement_picker() n'accepte-t-il que des Integers ?\n")

        product_pos = random.randint(0, Product.objects.count()-1)
        random_product = Product.objects.all()[product_pos]
        
        for types in [str(), bool(), list(), dict(), set(), bytes()]:
            with self.assertRaises(TypeError):
                substitute = replacement_picker(random_product, types, types)

    @tag("t2-p2")
    def test_if_the_replacement_product_is_better_from_a_nutrition_standpoint(self):
        print("\nTest 2 - (2/2) : replacement_picker() offre-t-il des produits au nutriscore équivalent ou meilleur?\n")

        products = Product.objects.all()

        for _ in range(20): 
            random_product = products[random.randint(0, products.count()-1)]
            substitute = replacement_picker(random_product, 0,1)[0] 

            self.assertLessEqual(
                ord(substitute.nutrition.nutriscore), 
                ord(random_product.nutrition.nutriscore))
