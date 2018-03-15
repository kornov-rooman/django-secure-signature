import typing as t

from django.conf import settings as dj_settings
from django.core.exceptions import ImproperlyConfigured

from .utils import import_from_string, transform_header_to_django_meta_format

AVAILABLE_SETTINGS = {
    # optional:
    'MAX_AGE',

    # mandatory:
    'HEADER',
    'SECRET',
    'SALT',
    'DATA_GENERATOR',

    # calculating
    'meta_formatted_header',
    'get_data',
}
DEFAULT_SETTINGS = {
    'MAX_AGE': None,
}
CALCULATING_SETTINGS = {
    'meta_formatted_header',
    'get_data',
}


class ItemSettings:
    def __init__(self, _settings: dict):
        self._settings = _settings

        self.available_settings = AVAILABLE_SETTINGS
        self.defaults = DEFAULT_SETTINGS
        self.calculating = CALCULATING_SETTINGS

    def __getattr__(self, attr: str) -> t.Any:
        if attr not in self.available_settings:
            raise AttributeError(f'Invalid setting: {attr}')

        if attr in self.calculating:
            val = self.calculate(attr)

            self.memorize(attr, val)
            return val

        try:
            val = self._settings[attr]
        except KeyError:
            val = self.defaults[attr]

        self.memorize(attr, val)
        return val

    def calculate(self, attr: str) -> t.Any:
        if attr == 'meta_formatted_header':
            return transform_header_to_django_meta_format(self.HEADER)

        if attr == 'get_data':
            if callable(self.DATA_GENERATOR):
                return self.DATA_GENERATOR
            elif isinstance(self.DATA_GENERATOR, str):
                return import_from_string(self.DATA_GENERATOR, 'DATA_GENERATOR')
            else:
                return lambda *args, **kwargs: self.DATA_GENERATOR

        assert False

    def memorize(self, attr: str, val: t.Any):  # in order to readability: explicit method definition
        setattr(self, attr, val)


class Settings:  # iterable settings
    def __init__(self, app_settings: t.Optional[dict] = None):
        self._settings = None
        self.reread_settings(app_settings)

    def __iter__(self):  # proxy
        return self._settings.__iter__()

    def reread_settings(self, app_settings: t.Optional[list] = None):
        if not app_settings:
            app_settings = getattr(dj_settings, 'DJANGO_SECURE_SIGNATURE', [])

        if not (isinstance(app_settings, list) or isinstance(app_settings, tuple)):
            msg = f'DJANGO_SECURE_SIGNATURE must be either a list or tuple, not {type(app_settings)}!'
            raise ImproperlyConfigured(msg)

        self._settings = [ItemSettings(item) for item in app_settings]
