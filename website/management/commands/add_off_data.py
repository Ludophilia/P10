import os, re, time

import requests
from django.core.management.base import BaseCommand, CommandError

from website.models import Product, Nutrition, Media

class OFFAPIManager:

    @classmethod
    def __get_categories(cls) -> list:
        file_path = os.path.join(os.path.dirname(__file__), "categories.txt")
        with open(file_path) as f: 
            return [category.replace("\n","") for category in list(f)]
    
    @classmethod
    def __get_list_of_products(cls, search_terms: str, page_size: int, page_number: int) -> list:
        
        search_pr = {"action": "process", 
        "search_terms": search_terms, 
        "tagtype_0":"categories", 
        "tag_contains_0":"contains", 
        "tag_0": search_terms, 
        "sort_by": "unique_scans_n", 
        "page_size": page_size, 
        "page": page_number, 
        "json": "true"}

        data = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params = search_pr)
        
        return data.json()["products"]

    @classmethod
    def __are_values_missing(cls, product: dict) -> bool: 

        try:
            if len(product["product_name_fr"]) != 0 and len(product["nutrition_grade_fr"]) != 0 and len(product["image_front_url"])!= 0 and product["nutriments"]["energy_100g"] >= 0:
                return False
        except:
            pass

        return True
        
    @classmethod
    def get_product_data(cls, product: dict, key: str) -> str:
        
        top_keys = ["category", "product_name_fr", "url", "nutrition_grade_fr", "image_full_url", "image_front_url"]
        try:
            if key in top_keys:
                return product[key] if key != "image_full_url" else product["image_front_url"].replace(".400.jpg", ".full.jpg")
            else:
                return str(product["nutriments"][key])
        except (KeyError):
            if re.search(r'^.{3,13}_100g$',key):
                return "-1"
            elif re.search(r'^.{3,13}_unit$',key):
                return "-"
    
    @classmethod
    def get_all_products(cls) -> list:

        all_products, watchdog_scope = [], []

        all_products_raw = [{"category": category, **product} for category in cls.__get_categories() 
            for product in cls.__get_list_of_products(category, 20, 1)
            if not cls.__are_values_missing(product)]

        for product in all_products_raw:
            product_name = cls.get_product_data(product, "product_name_fr")
            if product_name.capitalize() not in watchdog_scope:
                watchdog_scope += [product_name.capitalize()]
                all_products += [product]

        return all_products

class DBManager:

    @staticmethod
    def check_data_already_in_db() -> None:
        
        print(f"\n{time.strftime('%a %d/%m/%Y, %X')}: Vérification des données de produit dans la BDD...")
        
        products = Product.objects.all()
        deletions = 0

        if products.count() > 0:

            print(f"...{products.count()} produit(s) trouvés...\n...suppression des données corrompues...")

            for product in products:
                r = requests.get(product.off_url)
                if r.status_code != 200:
                    product.delete()
                    deletions += 1

            if deletions > 0:
                print(f"...{deletions} produit(s) supprimé(s).")
            
        if products == 0 or deletions == 0:
            print("0 donnée produit à supprimer.")

    @staticmethod
    def show_data(type_data: str) -> None:
        
        if type_data == "product_data":
            for product in Product.objects.all():
                print("Product:", product.product_name, product.category, product.off_url)
        
        if type_data == "media_data":
            for media in Media.objects.all():
                print("Media:", media.image_front_url, media.image_full_url)

        if type_data == "nutrition_data":
            for nutriment in Nutrition.objects.all():
                print("Nutrition:", nutriment.product, nutriment.nutriscore, nutriment.energy_100g, nutriment.energy_unit,
                nutriment.proteins_100g, nutriment.fat_100g, nutriment.saturated_fat_100g, nutriment.carbohydrates_100g, nutriment.sugars_100g, nutriment.fiber_100g, nutriment.salt_100g)

    @classmethod
    def __create_or_update_product_data(cls, product: dict) -> (Product, bool):
        
        product_entry, has_been_created = Product.objects.update_or_create(
            defaults = {
                'off_url' : OFFAPIManager.get_product_data(product, "url"),
                'category' : OFFAPIManager.get_product_data(product, "category")
            },
            product_name = OFFAPIManager.get_product_data(product, "product_name_fr")
        )

        return (product_entry, has_been_created)

    @classmethod
    def __create_or_update_media_data(cls, product_entry: Product, product: dict) -> None:

        Media.objects.update_or_create(
            product = product_entry,
            defaults = {
                'image_front_url' : OFFAPIManager.get_product_data(product, "image_front_url"),
                'image_full_url' : OFFAPIManager.get_product_data(product, "image_full_url")
            }
        )

    @classmethod
    def __create_or_update_nutrition_data(cls, product_entry: Product, product: dict) -> None:

        Nutrition.objects.update_or_create(
            product = product_entry,
            defaults = {
                'nutriscore' : OFFAPIManager.get_product_data(product, "nutrition_grade_fr"),
                'energy_unit' : OFFAPIManager.get_product_data(product, "energy_unit"),
                'energy_100g' : float(OFFAPIManager.get_product_data(product, "energy_100g")),
                'proteins_100g' : float(OFFAPIManager.get_product_data(product, "proteins_100g")),
                'fat_100g' : float(OFFAPIManager.get_product_data(product, "fat_100g")),
                'saturated_fat_100g' : float(OFFAPIManager.get_product_data(product, "saturated-fat_100g")),
                'carbohydrates_100g' : float(OFFAPIManager.get_product_data(product, "carbohydrates_100g")),
                'sugars_100g' : float(OFFAPIManager.get_product_data(product, "sugars_100g")),
                'fiber_100g' : float(OFFAPIManager.get_product_data(product, "fiber_100g")),
                'salt_100g' : float(OFFAPIManager.get_product_data(product, "salt_100g"))
            }
        )

    @classmethod
    def add_products_to_db(cls) -> None:

        print("\nMise à jour des données...")

        products_created = 0

        for product in OFFAPIManager.get_all_products():

            product_obj, product_created = cls.__create_or_update_product_data(product)
            cls.__create_or_update_media_data(product_obj, product)
            cls.__create_or_update_nutrition_data(product_obj, product)

            if product_created: products_created += 1

        print(f"...{products_created} nouveau(x) produit(s) ajoutés(s)...\
            \n{Product.objects.count()} produit(s) au total.\n")

class Command(BaseCommand):
    
    def handle(self, *args, **options) -> None: 
        
        DBManager.check_data_already_in_db()
        DBManager.add_products_to_db()

        # DBManager.show_data("product_data")
        # DBManager.show_data("media_data")
        # DBManager.show_data("nutrition_data")
