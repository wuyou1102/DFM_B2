# -*- encoding:UTF-8 -*-
import logging.config
import os
import time
from libs.Config.Path import CONSOLE_LOG_SAVE

backupCount = 10
logs = os.listdir(CONSOLE_LOG_SAVE)
logs.sort(reverse=True)
if len(logs) > backupCount:
    logs = logs[backupCount:]
for log in logs:
    os.remove(os.path.join(CONSOLE_LOG_SAVE, log))

timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
__LOG = os.path.join(CONSOLE_LOG_SAVE, "%s.log" % timestamp)


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
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': __LOG,
            'formatter': 'verbose',
            'encoding': 'utf8',
            'maxBytes': 1024 * 1024 * 100,
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
})
