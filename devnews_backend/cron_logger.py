import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'filters': {
        'info_filter': {
            '()': InfoFilter,
        },
    },

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },

    'handlers': {
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cron_info.log'),
            'formatter': 'verbose',
            'filters': ['info_filter'],
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cron_error.log'),
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'cron': {
            'handlers': ['info_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
