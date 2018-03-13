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
