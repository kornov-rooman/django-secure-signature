"""
DJANGO_SECURE_SIGNATURE = {
    'SALT': 'some-salt',
    'SECRET': 'some-secret',

    'DATA': {'test': 'test'},
}

OR

DJANGO_SECURE_SIGNATURE = [
    {
        'SIGNATURE_ID': '1',  # TODO: looks redundant

        'HEADER': 'X-Data-Signed-1',

        'SALT': 'salt-1',
        'SECRET': 'secret-1',

        'DATA': lambda request, *args, **kwargs: {'test': 'test'}
        'MAX_AGE': timedelta(seconds=60),
    },
    {
        'SIGNATURE_ID': '2',  # TODO: looks redundant

        'HEADER': 'X-Data-Signed-2',

        'SALT': 'salt-node-2',
        'SECRET': 'secret-node-2',

        'DATA': {'test': 'test'}
    },
    {
        'SIGNATURE_ID': '3',  # TODO: looks redundant

        'HEADER': 'X-Data-Signed-3',

        'SALT': 'salt-3',
        'SECRET': 'secret-3',

        'DATA': 'common.utils.get_data_for_signature'
    },
]
"""
from importlib import import_module
import typing as t

from django.conf import settings as dj_settings
from django.test.signals import setting_changed

APP_SETTINGS = {
    'SIGNATURE_ID',
    'HEADER',
    'meta_formatted_header',
    'SALT',  # mandatory
    'SECRET',  # mandatory
    'DATA',  # mandatory
    'data',
    'MAX_AGE',
}
CALCULATING_SETTINGS = {
    'meta_formatted_header',
    'data',
}
DEFAULT_SETTINGS = {
    'SIGNATURE_ID': '0',
    'HEADER': 'X-Data-Signed',
    'MAX_AGE': None,
}


class Settings:
    def __init__(self, defined_settings: t.Optional[dict]=None):
        if defined_settings:
            self._defined_settings = defined_settings

        self._memorized = set()

        self.app_settings = APP_SETTINGS
        self.calculating = CALCULATING_SETTINGS
        self.defaults = DEFAULT_SETTINGS

    def __getattr__(self, attr: str) -> t.Any:
        if attr not in self.app_settings:
            raise AttributeError(f'Invalid setting: {attr}')

        if attr in self.calculating:
            val = self.calculate(attr)

            self.memorize(attr, val)
            return val

        try:
            val = self.defined_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        self.memorize(attr, val)
        return val

    @property
    def defined_settings(self):
        if not hasattr(self, '_defined_settings'):
            defined_settings = getattr(dj_settings, 'DJANGO_SECURE_SIGNATURE', {})
            setattr(self, '_defined_settings', defined_settings)

        return getattr(self, '_defined_settings')

    def calculate(self, attr: str) -> t.Any:
        if attr == 'meta_formatted_header':
            return self.get_meta_formatted_header(self.HEADER)

        if attr == 'data':
            if callable(self.DATA):
                return self.DATA
            elif isinstance(self.DATA, str):
                return import_module(attr)
            else:
                return self.DATA

        assert False

    @staticmethod
    def get_meta_formatted_header(header: str) -> str:
        header = header.upper()
        header = header.replace('-', '_')

        return f'HTTP_{header}'

    def memorize(self, attr: str, val: t.Any):
        self._memorized.add(attr)
        setattr(self, attr, val)

    def forget(self):
        for attr in self._memorized:
            delattr(self, attr)

        self._memorized.clear()

        if hasattr(self, '_defined_settings'):
            delattr(self, '_defined_settings')


settings = Settings()


# noinspection PyUnusedLocal
def drop_settings(*args, **kwargs):
    if kwargs['setting'] == 'DJANGO_SECURE_SIGNATURE':
        settings.forget()


setting_changed.connect(drop_settings)
