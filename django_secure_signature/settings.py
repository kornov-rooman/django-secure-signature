"""
DJANGO_SECURE_SIGNATURE = [
    {
        'HEADER': 'X-Custom-Header',

        'SECRET': 'secret-1',
        'SALT': 'salt-1',

        'DATA_GENERATOR': lambda request, *args, **kwargs: {'test': 'test'}

        'MAX_AGE': timedelta(seconds=60),
    },
    {
        'HEADER': 'X-Signed-Header',

        'SECRET': 'secret-2',
        'SALT': 'salt-2',

        'DATA_GENERATOR': {'test': 'test'}
    },
    {
        'HEADER': 'X-Special-Header',

        'SECRET': 'secret-3',
        'SALT': 'salt-3',

        'DATA_GENERATOR': 'common.utils.get_data_for_signature'

        'MAX_AGE': 3600,
    },
]
"""
from django.test.signals import setting_changed

from ._settings import Settings

settings = Settings()


# noinspection PyUnusedLocal
def drop_settings(*args, **kwargs):
    if kwargs['setting'] == 'DJANGO_SECURE_SIGNATURE':
        settings.reread_settings()


setting_changed.connect(drop_settings)
