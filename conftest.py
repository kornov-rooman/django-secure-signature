from datetime import timedelta
import os

import pytest


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.django_app')


@pytest.fixture(scope='session')
def data_for_signing():
    return {'uid': 5432}


@pytest.fixture(scope='session')
def signed_data():
    return 'eyJ1aWQiOjU0MzJ9:1evlue:XhyDA7Z6e7nTOD0jpIZH_lB8_LQ:1evlue:TJV81AtFxFiDdUm2HYYgIQv6NKs'


@pytest.fixture(scope='session')
def compromised_data():
    return '1eyJ1aWQiOjU0MzJ9:1evlue:XhyDA7Z6e7nTOD0jpIZH_lB8_LQ:1evlue:TJV81AtFxFiDdUm2HYYgIQv6NKs'


# noinspection PyShadowingNames
@pytest.fixture(scope='function')
def settings__sing_middleware(settings, data_for_signing):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.SignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = {
        'SALT': 'salt',
        'SECRET': 'secret',
        'TARGET': lambda *args, **kwargs: data_for_signing
    }
    return settings


@pytest.fixture(scope='function')
def settings__unsign_middleware(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.UnsignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = {
        'SALT': 'salt',
        'SECRET': 'secret',
    }
    return settings


@pytest.fixture(scope='function')
def settings__unsign_middleware__with_max_age(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.UnsignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = {
        'SALT': 'salt',
        'SECRET': 'secret',
        'MAX_AGE': 5
    }
    return settings


@pytest.fixture(scope='function')
def settings__sign_middleware__01(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.UnsignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = [
        {
            'HEADER': 'X-Data-Signed-1',

            'SALT': 'salt-node-1',
            'SECRET': 'secret-node-1',

            'MAX_AGE': timedelta(seconds=60),
            'DATA': lambda request, *args, **kwargs: {'test': 'test'}
        },
        {
            'HEADER': 'X-Data-Signed-2',

            'SALT': 'salt-node-2',
            'SECRET': 'secret-node-2',

            'MAX_AGE': timedelta(seconds=60),
            'DATA': {'test': 'test'}
        },
        {
            'HEADER': 'X-Data-Signed-3',

            'SALT': 'salt-node-3',
            'SECRET': 'secret-node-3',

            'DATA': 'common.utils.get_data_for_signature'
        },
    ]

    return settings
