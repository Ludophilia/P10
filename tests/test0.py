from django.test import SimpleTestCase, tag 
import requests

@tag("t0")
class TestWebsiteAccess(SimpleTestCase):
    
    @tag("t0-p1")
    def test_if_the_user_cant_reach_the_original_website_address(self):

        print("\n1/2 - Test de connexion: http://178.62.50.10 est-il toujours accessible ? Renvoie-t-il bien une erreur 444 ?\n")
        
        with self.assertRaises(requests.exceptions.ConnectionError):
            r = requests.get("http://178.62.50.10")
            self.assertEqual(r.status_code, 444) 

    @tag("t0-p2")
    def test_if_the_user_is_correctly_redirected_to_the_https_version_of_the_site(self):
        
        print("\n2/2 - Test de redirection: contacter purbeurre.space via http génère-t-il bien une code 301 ? Est-on bien redirigé vers la version https du site ?\n")

        for url in ["purbeurre.space/", "www.purbeurre.space/"]:
            request = requests.get("http://" + url)

            self.assertEqual(request.history[0].status_code, 301) #On teste qu'il y a bien eu redirection
            self.assertEqual(request.status_code, 200) #Est-on bien arrivé quelque part ? 
            self.assertEqual(request.url, "https://" + url) # Sur la version https ?
