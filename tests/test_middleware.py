import pytest

from django.urls import reverse

pytestmark = pytest.mark.middleware

DATA = {'uid': 5432}
SIGNATURE = 'eyJ1aWQiOjU0MzJ9:1ewX1j:L_ZB9w4KIamcHP6L9vr9I58GYmY'
COMPROMISED_SIGNATURE = 'eyJ1aWQiOjU0MzJ9:1ewX56:BR50grR1AyQTR7_3NYw_ceXMdow'


@pytest.fixture
def settings_single_signature__sign(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.SignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = [{
        'HEADER': 'X-Data-Secure-Signed',
        'SALT': 'salt',
        'SECRET': 'secret',
        'DATA_GENERATOR': DATA
    }]

    return settings


@pytest.fixture
def settings_single_signature__unsign(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.UnsignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = [{
        'HEADER': 'X-Unsign-Only',
        'SALT': 'salt',
        'SECRET': 'secret',
        'DATA_GENERATOR': DATA
    }]

    return settings


@pytest.fixture
def settings_single_signature__unsign__with_max_age(settings):
    settings.MIDDLEWARE = [
        'django_secure_signature.middleware.UnsignMiddleware',
    ]
    settings.DJANGO_SECURE_SIGNATURE = [{
        'HEADER': 'X-Signed-Perishable',
        'SALT': 'salt',
        'SECRET': 'secret',
        'DATA_GENERATOR': DATA,
        'MAX_AGE': 1
    }]

    return settings


# noinspection PyUnusedLocal
def test_can_sign_data(client, settings_single_signature__sign):
    url = reverse('index1')
    response = client.get(url)

    assert response.status_code == 200
    assert response.has_header('X-Data-Secure-Signed')

    data = response.json()['data']
    assert len(data) == 1
    assert response['X-Data-Secure-Signed'] == data['X-Data-Secure-Signed']


# noinspection PyUnusedLocal
def test_can_confirm_data(client, settings_single_signature__unsign):
    url = reverse('index2')
    response = client.get(url, HTTP_X_UNSIGN_ONLY=SIGNATURE)

    assert response.status_code == 200

    data = response.json()['data']
    assert len(data) == 1
    assert data[0] == DATA


# noinspection PyUnusedLocal
def test_signature_does_not_match(client, settings_single_signature__unsign):
    url = reverse('index2')
    response = client.get(url, HTTP_X_UNSIGN_ONLY=COMPROMISED_SIGNATURE)

    assert response.status_code == 403


# noinspection PyUnusedLocal
def test_signature_expired(client, settings_single_signature__unsign__with_max_age):
    url = reverse('index2')
    response = client.get(url, HTTP_X_SIGNED_PERISHABLE=SIGNATURE)

    assert response.status_code == 403
