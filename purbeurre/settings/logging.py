import os

import raven

RAVEN_CONFIG = {
    'dsn': f'https://{os.environ.get("SENTRY_DSN")}',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['sentry', 'console'],
    },
    'loggers': {
        'website.views': {
            'level': 'DEBUG',
            'handlers': ['sentry', 'console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter'
        },
        'sentry': {
            'level': 'INFO', 
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'the_freshest_tag'},
        },
    },
    'formatters': {
        'default_formatter': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                        '- %(message)s' #%(process)d %(thread)d
        },
    },
}