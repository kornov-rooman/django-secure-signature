import pytest

from django.urls import reverse


# noinspection PyUnusedLocal
@pytest.mark.skip
def test_response_headers(client, settings__sing_middleware):
    url = reverse('index1')
    response = client.get(url)

    assert response.status_code == 200
    assert response.has_header('X-Data-Signed')
    assert response['X-Data-Signed'] == response.json()['signed_data']


# noinspection PyUnusedLocal
@pytest.mark.skip
def test_request_has_attr(client, settings__unsign_middleware, data_for_signing, signed_data):
    url = reverse('index2')
    response = client.get(url, HTTP_X_DATA_SIGNED=signed_data)

    assert response.status_code == 200
    assert response.json()['confirmed_signed_data'] == data_for_signing


# noinspection PyUnusedLocal
@pytest.mark.skip
def test_signature__expired(client, settings__unsign_middleware__with_max_age, signed_data):
    url = reverse('index2')
    response = client.get(url, HTTP_X_DATA_SIGNED=signed_data)

    assert response.status_code == 403


# noinspection PyUnusedLocal
@pytest.mark.skip
def test_signature__does_not_match(client, settings__unsign_middleware, compromised_data):
    url = reverse('index2')
    response = client.get(url, HTTP_X_DATA_SIGNED=compromised_data)

    assert response.status_code == 403


def test_01(client, settings__unsign_middleware, compromised_data):
    url = reverse('index2')
    response = client.get(url, HTTP_X_DATA_SIGNED=compromised_data)

    assert response.status_code == 403