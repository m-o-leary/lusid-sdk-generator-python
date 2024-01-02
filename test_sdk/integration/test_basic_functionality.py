from lusid.extensions import (
    ApiClientFactory,
    SyncApiClientFactory,
    EnvironmentVariablesConfigurationLoader,
)
from lusid.api import ApplicationMetadataApi
from lusid.api_response import ApiResponse
import pytest


class TestSyncApiClient:
    def test_get_application_metadata(self):
        api_client_factory = SyncApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
            tcp_keep_alive=False,
        )
        with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = api_instance.get_lusid_versions_with_http_info()
            assert response.status_code == 200
            assert isinstance(response, ApiResponse)

    def test_get_application_metadata_with_preload_content_false(self):
        api_client_factory = SyncApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
            tcp_keep_alive=False,
        )
        with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = api_instance.get_lusid_versions_with_http_info(
                _preload_content=False
            )
            assert response.status_code == 200
            assert isinstance(response, ApiResponse)

    def test_get_application_metadata_with_return_http_data_only_true(self):
        api_client_factory = SyncApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
            tcp_keep_alive=False,
        )
        with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = api_instance.get_lusid_versions_with_http_info(
                _return_http_data_only=True,
                _preload_content=False
            )
            assert not isinstance(response, ApiResponse)


class TestASyncApiClient:
    @pytest.mark.asyncio
    async def test_get_application_metadata(self):
        api_client_factory = ApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
        )
        async with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = await api_instance.get_lusid_versions_with_http_info()
            assert response.status_code == 200
            assert isinstance(response, ApiResponse)

    @pytest.mark.asyncio
    async def test_get_application_metadata_with_preload_content_false(self):
        api_client_factory = ApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
        )
        async with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = await api_instance.get_lusid_versions_with_http_info(
                _preload_content=False
            )
            assert response.status_code == 200
            assert isinstance(response, ApiResponse)

    @pytest.mark.asyncio
    async def test_get_application_metadata_with_return_http_data_only_true(self):
        api_client_factory = ApiClientFactory(
            app_name="test_sdk",
            config_loaders=[EnvironmentVariablesConfigurationLoader()],
        )
        async with api_client_factory:
            api_instance = api_client_factory.build(ApplicationMetadataApi)
            response = await api_instance.get_lusid_versions_with_http_info(
                _preload_content=False,
                _return_http_data_only=True
            )
            assert not isinstance(response, ApiResponse)
