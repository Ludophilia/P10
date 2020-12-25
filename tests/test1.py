import os
from decimal import Decimal

from django.test import TestCase, tag 
from django.core.management import call_command

from website.management.commands.add_off_data import Command
from website.models import Product, Nutrition, Media

@tag("t1")
class TestProductAdditionAndUpdateToDatabase(TestCase):
    
    def setUp(self):
        Command().handle() #call_command('loaddata', 'website/dumps/website.json') #Charge de vieilles données pour voir comment mon code réagit à la mise à jour

    def get_categories_from_categories_txt(self):
        with open(os.path.join("website", "management", "commands", "categories.txt")) as f: 
            return [category.replace("\n","") for category in list(f)]   
            
    @tag("t1-p1")
    def test_if_data_has_been_added(self):
        
        print("\n1/4 - Test d'ajout: les produits ont-ils bien été ajoutés ? Y'a-t-il le meme nombre de produits dans chaque table ? Y'a-t-il plus de 15 produits par catégorie ?\n")

        total_products, total_nutrition, total_media = Product.objects.count(), Nutrition.objects.count(), Media.objects.count()

        for _ in [total_products, total_nutrition, total_media]: 
            self.assertGreaterEqual(_, 36*15) 

        self.assertEqual(total_products, total_nutrition)
        self.assertEqual(total_nutrition, total_media)

        print(f"Total - Product: {total_products}, Nutrition: {total_nutrition}, Media: {total_media} - Données uniformes, vous pouvez y aller!\n") 

    @tag("t1-p2")
    def test_the_quality_of_product_data(self):

        print("\n2/4 - Test de qualité données : les produits ont-ils bien un nom ? Appartiennent-ils à une catégorie valide ? Ont-ils une adresse off valide?\n")

        for product in Product.objects.all():
            self.assertNotEqual(len(product.product_name), 0) 
            self.assertIn(product.category,  self.get_categories_from_categories_txt())
            self.assertIn("https://fr.openfoodfacts.org/produit/", product.off_url)
    
    @tag("t1-p3")
    def test_the_quality_of_media_data(self):

        print("\n3/4 - Test de qualité données : les images ont-elles un format d'url valide ?\n")

        for media in Media.objects.all():
            for field in [media.image_full_url, media.image_front_url]:
                self.assertIn("https://static.openfoodfacts.org/images/products/", field)
                self.assertIn("full" if field == media.image_full_url else "400", field)

    @tag("t1-p4")
    def test_the_quality_of_nutrition_data(self):
        
        print("\n4/4 - Test de qualité données : les données nutritionneles ont-elles un format valide ?\n")

        for nutrition in Nutrition.objects.all():

            nutrition_fields = [nutrition.energy_100g, nutrition.proteins_100g, nutrition.fat_100g,
            nutrition.saturated_fat_100g, nutrition.carbohydrates_100g, nutrition.sugars_100g,
            nutrition.fiber_100g, nutrition.salt_100g]

            self.assertIn(nutrition.nutriscore, "abcdef")
            self.assertRegex(nutrition.energy_unit, r"^[kK]([Cc][Aa][Ll]|[Jj])$")

            for field in nutrition_fields:
                self.assertEqual(type(field), Decimal)
                self.assertGreaterEqual(field if field != nutrition.fiber_100g else 1, 0)
