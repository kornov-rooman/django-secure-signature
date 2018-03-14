import pytest

from django_secure_signature.settings import Settings

pytestmark = pytest.mark.settings


def test_single_settings__defaults():
    settings = Settings()

    assert settings._0.SIGNATURE_ID == '0'
    assert settings._0.HEADER == 'X-Data-Signed'
    assert settings._0.MAX_AGE is None


def test_single_settings__defaults__ok():
    defined = {
        'SALT': 'some-salt',
        'SECRET': 'some-secret',

        'DATA': {'test': 'test'},
    }
    settings = Settings(defined)

    assert settings.SALT == 'some-salt'
    assert settings.SECRET == 'some-secret'
    assert settings.data == {'test': 'test'}
    assert settings.meta_formatted_header == 'HTTP_X_DATA_SIGNED'


def test_single_settings__defaults__fail():
    settings = Settings()

    with pytest.raises(KeyError):
        assert settings.SALT

    with pytest.raises(KeyError):
        assert settings.SECRET

    with pytest.raises(KeyError):
        assert settings.data
