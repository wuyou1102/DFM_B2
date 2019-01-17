# -*- encoding:UTF-8 -*-
import logging.config
import os
import sys

__LOG = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "console.log")

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': __LOG,
            'formatter': 'verbose',
            'encoding': 'utf8',
            'maxBytes': 1024 * 1024 * 1,
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
})
