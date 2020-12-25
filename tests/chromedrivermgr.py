import os, zipfile

import wget
from selenium import webdriver

class ChromeDriverMgr():

    @classmethod
    def get_chromedriver(cls, os_name, version):

        """ Automatise le téléchargement du chromedriver et le renvoie pour utilisation """
        
        # GET CHROMEDRIVER : https://sites.google.com/a/chromium.org/chromedriver/

        dirname = os.path.dirname(os.path.abspath(__file__))
        build_path = lambda filename: os.path.join(dirname, filename)

        if not os.path.exists(build_path("chromedriver")):
            
            ext = {"mac": "mac64", "win": "win32"}.get(os_name)
            chromedriver_url = f"http://chromedriver.storage.googleapis.com/{version}/chromedriver_{ext}.zip"

            wget.download(chromedriver_url, build_path("chromedriver.zip"))

            with zipfile.ZipFile(build_path("chromedriver.zip"), mode="r") as z:
                chromedriver = z.getinfo("chromedriver") #Python 3.8. Use := (walrus) to assign and return ?
                z.extract(chromedriver, path=build_path(""))
            
            os.system(f"chmod 755 {build_path('chromedriver')}")
            os.remove(build_path("chromedriver.zip"))

        return webdriver.Chrome(build_path('chromedriver'))