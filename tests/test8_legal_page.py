from django.test import TestCase, tag, Client
from django.urls import reverse

@tag("t8")
class TestLegalPage(TestCase):
    
    @tag("t8-p1")
    def test_if_the_webpage_is_correctly_displayed(self):

        print("\nTest 8 - (1/1) : La page de mentions légales est-elle accessible ?\n")

        self.client = Client()
        self.response = self.client.get(reverse("legal"))
        self.assertEqual(self.response.status_code, 200) 