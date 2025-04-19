import pytest
from unittest.mock import MagicMock, patch
import valkey.exceptions
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from src import CacheService

@pytest.fixture(autouse=True)
def reset_singleton():
    # Reset the singleton before each test
    CacheService._CacheService__shared_instance = None
    yield
    CacheService._CacheService__shared_instance = None

@patch('valkey.from_url')
def test_get_instance_cache_disabled(mock_from_url):
    service = CacheService.getInstance("redis://localhost", isCacheDisabled=True, expirationTime=3600)
    assert service is None
    mock_from_url.assert_not_called()

@patch('valkey.from_url')
def test_get_instance_first_time(mock_from_url):
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    
    assert service is not None
    assert isinstance(service, CacheService)
    mock_from_url.assert_called_once()

@patch('valkey.from_url')
def test_get_instance_already_exists(mock_from_url):
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_from_url.return_value = mock_client

    first_service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    second_service = CacheService.getInstance("redis://another", isCacheDisabled=False, expirationTime=9999)

    assert first_service is second_service
    mock_from_url.assert_called_once()  # Only one real connection is made

@patch('valkey.from_url')
def test_init_authentication_error(mock_from_url):
    mock_from_url.side_effect = valkey.exceptions.AuthenticationError

    with pytest.raises(Exception) as excinfo:
        CacheService.getInstance("invalid-url", isCacheDisabled=False, expirationTime=3600)

    assert "connection failed" in str(excinfo.value).lower()

@patch('valkey.from_url')
def test_get_method(mock_from_url):
    mock_client = MagicMock()
    mock_client.get.return_value = b'cached_value'
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    value = service.get('my_key')

    assert value == 'cached_value'
    mock_client.get.assert_called_once_with('my_key')

@patch('valkey.from_url')
def test_get_method_none(mock_from_url):
    mock_client = MagicMock()
    mock_client.get.return_value = None
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    value = service.get('missing_key')

    assert value is None
    mock_client.get.assert_called_once_with('missing_key')

@patch('valkey.from_url')
def test_set_method(mock_from_url):
    mock_client = MagicMock()
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    service.set('new_key', 'new_value')

    mock_client.setex.assert_called_once_with('new_key', 3600, 'new_value')

@patch('valkey.from_url')
def test_exist_method(mock_from_url):
    mock_client = MagicMock()
    mock_client.exists.return_value = 1
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    exists = service.exist('existing_key')

    assert exists is True
    mock_client.exists.assert_called_once_with('existing_key')

@patch('valkey.from_url')
def test_not_exist_method(mock_from_url):
    mock_client = MagicMock()
    mock_client.exists.return_value = 0
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=3600)
    exists = service.exist('missing_key')

    assert exists is False
    mock_client.exists.assert_called_once_with('missing_key')

@patch('valkey.from_url')
def test_get_expiration_time_formatting(mock_from_url):
    mock_client = MagicMock()
    mock_from_url.return_value = mock_client

    service = CacheService.getInstance("redis://localhost", isCacheDisabled=False, expirationTime=93784) # 1 day 2 h 3 mn 4 s
    output = service.getExpirationTime()

    assert output == "1 d 2 h 3 mn 4 s"
