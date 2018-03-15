import pytest

# noinspection PyProtectedMember
from django_secure_signature._settings import ItemSettings

pytestmark = [pytest.mark.unit, pytest.mark.settings]


def test_item_settings__with_defaults():
    defined = {
        'HEADER': 'X-Data-Secure-Signed',
        'SECRET': 'secret',
        'SALT': 'salt',
        'DATA_GENERATOR': {'test': 'test'}
    }
    settings = ItemSettings(defined)

    assert settings.HEADER == 'X-Data-Secure-Signed'
    assert settings.MAX_AGE is None

    assert settings.SECRET == 'secret'
    assert settings.SALT == 'salt'
    assert settings.DATA_GENERATOR == {'test': 'test'}

    assert settings.meta_formatted_header == 'HTTP_X_DATA_SECURE_SIGNED'
    assert settings.get_data() == {'test': 'test'}


def test_item_settings():
    defined = {
        'HEADER': 'X-Test',
        'MAX_AGE': 3600,
        'SECRET': 'secret-1',
        'SALT': 'salt-1',
        'DATA_GENERATOR': lambda: 'test',
    }
    settings = ItemSettings(defined)

    assert settings.HEADER == 'X-Test'
    assert settings.MAX_AGE == 3600

    assert settings.SECRET == 'secret-1'
    assert settings.SALT == 'salt-1'
    assert settings.DATA_GENERATOR() == 'test'

    assert settings.meta_formatted_header == 'HTTP_X_TEST'
    assert settings.get_data() == 'test'


def test_item_settings__fail():
    settings = ItemSettings({})

    with pytest.raises(KeyError):
        assert settings.HEADER

    with pytest.raises(KeyError):
        assert settings.SECRET

    with pytest.raises(KeyError):
        assert settings.SALT

    with pytest.raises(KeyError):
        assert settings.DATA_GENERATOR


def test_item_settings__data_generator():
    # 1. python path
    settings = ItemSettings({
        'DATA_GENERATOR': 'tests.django_app.custom_data_generator'
    })

    assert settings.get_data() == 'test'

    # 2. callable
    settings = ItemSettings({
        'DATA_GENERATOR': lambda: 'test2'
    })

    assert settings.get_data() == 'test2'

    # 3. some data
    settings = ItemSettings({
        'DATA_GENERATOR': [1, 2, 3]
    })

    assert settings.get_data() == [1, 2, 3]

    # 4. just None
    settings = ItemSettings({
        'DATA_GENERATOR': None
    })

    assert settings.get_data() is None
