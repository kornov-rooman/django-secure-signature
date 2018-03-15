"""
DJANGO_SECURE_SIGNATURE = [
    {
        'TARGET': 'http://example.com',

        'HEADER': 'X-Custom-Signed-Header',

        'SECRET': 'secret-1',
        'SALT': 'salt-1',

        'DATA': lambda request, *args, **kwargs: {'test': 'test'}
        'MAX_AGE': timedelta(seconds=60),
    },
    {
        'ORIGINATOR': 'http://first.example.com',

        'SECRET': 'secret-2',
        'SALT': 'salt-2',

        'DATA': {'test': 'test'}
    },
    {
        'SECRET': 'secret-3',
        'SALT': 'salt-3',

        'DATA': 'common.utils.get_data_for_signature'
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
