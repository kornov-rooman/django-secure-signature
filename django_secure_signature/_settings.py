from importlib import import_module
import typing as t

from django.conf import settings as dj_settings

AVAILABLE_SETTINGS = {
    # optional:
    'SENDER',
    'RECIPIENT',
    'HEADER',
    'MAX_AGE',

    # mandatory:
    'SECRET',
    'SALT',
    'DATA_GENERATOR',

    # calculating
    'meta_formatted_header',
    'get_data',
}
DEFAULT_SETTINGS = {
    'SENDER': None,
    'RECIPIENT': None,
    'HEADER': 'X-Data-Secure-Signed',
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
            return self.get_meta_formatted_header(self.HEADER)

        if attr == 'get_data':
            if callable(self.DATA_GENERATOR):
                return self.DATA_GENERATOR
            elif isinstance(self.DATA_GENERATOR, str):
                return import_module(attr)
            else:
                return lambda *args, **kwargs: self.DATA_GENERATOR

        assert False

    @staticmethod
    def get_meta_formatted_header(header: str) -> str:
        header = header.upper()
        header = header.replace('-', '_')

        return f'HTTP_{header}'

    def memorize(self, attr: str, val: t.Any):  # in order to readability: explicit method definition
        setattr(self, attr, val)


class Settings:  # iterable settings
    def __init__(self, app_settings: t.Optional[dict] = None):
        self._settings = None
        self.reread_settings(app_settings)

    def __iter__(self):  # proxy
        return self._settings.__iter__()

    def checks(self):  # TODO: ?
        """
        Warns a user if there's some validation errors.

            1. all headers must be unique
        """
        pass

    def reread_settings(self, app_settings: t.Optional[dict] = None):
        if not app_settings:
            app_settings = getattr(dj_settings, 'DJANGO_SECURE_SIGNATURE')

        self._settings = [ItemSettings(item) for item in app_settings]
