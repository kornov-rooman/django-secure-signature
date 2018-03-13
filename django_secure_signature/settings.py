from django.conf import settings as dj_settings
from django.test.signals import setting_changed

"""
# TODO:

SECURE_SIGNED = [
    {
        'HEADER': 'x-application-signed-data',
        'SECRET': 'some-secret',
        'SALT': 'some-salt',
        'TARGET': 'varname' or (lambda request, data: request)
        'SILENT': True,
    },
]
"""


class Settings:
    """
    DJANGO_SECURE_SIGNATURE = {
        'SALT': 'salt',
        'SECRET': 'secret',
        'HEADER': 'X-Data-Signed',
        'MAX_AGE': timedelta(days=1),
        'TARGET': lambda request, *args, *kwargs: {'test': 'test'}
    }
    """
    def __init__(self):
        self.attrs = {'SALT', 'SECRET', 'HEADER', 'MAX_AGE', 'TARGET', 'META_FORMATTED_HEADER', 'SHOULD_SIGN_DATA'}
        self.mandatory_attrs = {'SALT', 'SECRET'}

        self.defaults = {
            # SEE: https://tools.ietf.org/html/rfc6648
            'HEADER': 'X-Data-Signed',
            'MAX_AGE': None,
            'TARGET': None,
        }

        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.attrs:
            raise AttributeError(f'Invalid setting: {attr}')

        # TODO: hardcoded
        if attr == 'META_FORMATTED_HEADER':
            header = self.HEADER
            val = f'HTTP_{header.upper().replace("-", "_")}'
        elif attr == 'SHOULD_SIGN_DATA':
            val = callable(self.TARGET)
        else:
            try:
                val = self.user_settings[attr]
            except KeyError:
                if attr in self.mandatory_attrs:
                    raise AttributeError(f'Mandatory setting\'s key: {attr}')
                val = self.defaults[attr]

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    # noinspection PyAttributeOutsideInit
    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(dj_settings, 'DJANGO_SECURE_SIGNATURE', {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


settings = Settings()


# noinspection PyUnusedLocal
def reload_settings(*args, **kwargs):
    setting = kwargs['setting']

    if setting == 'DJANGO_SECURE_SIGNATURE':
        settings.reload()


setting_changed.connect(reload_settings)
