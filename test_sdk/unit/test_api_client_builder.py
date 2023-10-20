from lusid.extensions.api_client_builder import _get_access_token, build_client
from lusid.extensions.api_configuration import ApiConfiguration
from lusid.api_client import ApiClient as AsyncApiClient
from lusid.extensions.api_client import SyncApiClient
from lusid.extensions.proxy_config import ProxyConfig
from unittest.mock import patch
import pytest


@pytest.fixture
def patch_get_access_token():
    with patch(
        "lusid.extensions.api_client_builder._get_access_token",
        return_value="fake_token",
    ):
        yield


def test_get_access_token_with_access_token_and_url_returns_access_token():
    expected_result = "test_token"
    config = ApiConfiguration(access_token=expected_result, api_url="bla")
    result = _get_access_token(config)
    assert result == expected_result


def test_get_access_token_with_OIDC_params_returns_refreshing_token():
    config = ApiConfiguration(
        api_url="bla",
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
    )
    with patch(
        "lusid.extensions.api_client_builder.RefreshingToken"
    ) as mock_refreshing_token:
        _get_access_token(config)
        mock_refreshing_token.assert_called_once_with(
            api_configuration=config, id_provider_response_handler=None
        )


def test_get_acccess_token_without_access_token_and_OIDC_params_raises_ValueError():
    config = ApiConfiguration()
    with pytest.raises(ValueError):
        _get_access_token(config)


def test_build_client_without_api_url_raises_ValueError():
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
    )
    with pytest.raises(ValueError):
        build_client(api_config=config)

@pytest.mark.asyncio
async def test_build_client_returns_async_client(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url"
    )

    api_client = build_client(
        api_config=config,
        build_async_client=True,
    )
    assert isinstance(api_client, AsyncApiClient)


def test_build_client_returns_sync_client(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url"
    )

    api_client = build_client(
        api_config=config,
        build_async_client=False,
    )
    assert isinstance(api_client, SyncApiClient)


def test_build_client_with_tcp_keep_alive_sets_default_socket_options(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url"
    )
    mock_socket_options = [('some_level', 'some_option', 'some_value')]
    with patch('lusid.extensions.api_client_builder.keep_alive_socket_options', return_value=mock_socket_options):
        api_client = build_client(
            api_config=config, build_async_client=False, tcp_keep_alive=True
        )
        assert api_client.configuration.socket_options == mock_socket_options


def test_build_client_with_proxy_config_sets_proxy_config_on_api_client(patch_get_access_token):
    expected_address = 'http://sample_proxy_address'
    expected_username = 'sample_proxy_username'
    expected_password = 'sample_proxy_password'

    proxy_config = ProxyConfig(expected_address, expected_username, expected_password)

    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url",
        proxy_config=proxy_config
    )

    api_client = build_client(
        api_config=config, build_async_client=False, tcp_keep_alive=True
    )
    assert (
        api_client.configuration.proxy == expected_address
    )
    assert api_client.configuration.proxy_headers == proxy_config.headers


def test_build_client_with_correlation_id_sets_correlation_id_header(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url"
    )

    api_client = build_client(
        api_config=config, build_async_client=False, correlation_id="sample_correlation_id"

    )
    assert "sample_correlation_id" == api_client.default_headers["CorrelationId"]


def test_build_client_with_app_name_sets_app_name_header(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="fake_url"
    )

    api_client = build_client(
        api_config=config, build_async_client=False, app_name="sample_app_name"

    )
    assert "sample_app_name" == api_client.default_headers["X-LUSID-Application"]


def test_build_client_with_api_url_sets_api_client_host(patch_get_access_token):
    config = ApiConfiguration(
        password="password",
        username="me",
        client_id="test_id",
        client_secret="shhhh",
        token_url="fake_url",
        api_url="sample_api_url"
    )

    api_client = build_client(
        api_config=config, build_async_client=False, app_name="sample_app_name"

    )
    assert "sample_api_url" == api_client.configuration.host
