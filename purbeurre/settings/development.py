"""Django development settings for purbeurre project.""" 

from . import * #from <current_package> #Imports code in __init__.py.
from .logging import RAVEN_CONFIG, LOGGING, RAVEN_INSTALLED_APP

INSTALLED_APPS += RAVEN_INSTALLED_APP

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pur_beurre',
        'USER': 'P8',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432'
    }
}