from lusid.extensions.tcp_keep_alive_connector import TcpKeepAliveConnector
from unittest import mock
import pytest


class TestTCPKeepAliveConnector:
    @pytest.mark.asyncio
    async def test_create_connection_sets_sock_opts(self):
        mock_req = mock.MagicMock()
        mock_req.proxy = False
        mock_transport = mock.MagicMock()
        mock_socket = mock.MagicMock()
        mock_transport.get_extra_info.return_value = mock_socket
        mock_self = mock.MagicMock()
        mock_self._create_direct_connection = mock.AsyncMock(
            return_value=(mock_transport, None)
        )
        mock_self.socket_options = [(0, 1, 1)]
        await TcpKeepAliveConnector._create_connection(mock_self, mock_req, None, None)
        mock_socket.setsockopt.assert_called_once_with(0, 1, 1)
