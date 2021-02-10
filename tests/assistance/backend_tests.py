import random

from django.test import TestCase
from django.core.management import call_command

from website.models import Product

class AssistanceClassForTC(TestCase):

    def setUp(self) -> None:

        call_command("loaddata", "website/dumps/dump.json")

    def get_random_products(self, amount: int, text_only: bool = False) -> list:

        index_scope = (0, Product.objects.count()-1)
        roll_dice = lambda : random.randint(*index_scope)
        all_products = Product.objects.all()

        list_of_products = [all_products[roll_dice()].product_name.replace("  ", " ") if text_only else all_products[roll_dice()] for _ in range(amount)]

        return list_of_products