import copy

from populus.utils.networking import (
    wait_for_connection,
    get_open_port,
)

from .base import (
    BaseTesterChain,
)


class TestRPCChain(BaseTesterChain):
    port = None

    def get_web3_config(self):
        base_config = super(TestRPCChain, self).get_web3_config()
        config = copy.deepcopy(base_config)
        config['provider.settings.port'] = self.port
        return config

    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        if self.port is None:
            self.port = get_open_port()

        self._running = True

        self.provider = self.web3.currentProvider
        self.rpc_methods = self.provider.server.application.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        wait_for_connection('127.0.0.1', self.port)
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.provider.server.stop()
            self.provider.server.close()
            self.provider.thread.kill()
        except AttributeError:
            self.provider.server.shutdown()
            self.provider.server.server_close()
        finally:
            self._running = False