import enumerator
from logger import AppLog
from httpbrowser import http_browser, Requestor
from dataclasses import dataclass
import pandas as pd
import configsettings as cs


@dataclass
class SwapAPI:

    api_domain: str = ''
    pool_address: str = ''
    config_settings: cs.ConfigSettings = None

    def __post_init__(self):
        if self.config_settings.chain == enumerator.Chains.Ethereum:
            self.api_domain = 'https://swap-api.teahouse.finance/eth/'

        elif self.config_settings.chain == enumerator.Chains.ArbitrumL2:
            self.api_domain = 'https://swap-api.teahouse.finance/arb1/'

        elif self.config_settings.chain == enumerator.Chains.Polygon:
            self.api_domain = 'https://swap-api.teahouse.finance/poly/'

        elif self.config_settings.chain == enumerator.Chains.Optimism:
            self.api_domain = 'https://swap-api.teahouse.finance/opt/'

    def fetch_dex_tx(self, start_unix, end_unix):

        base_url = self.api_domain + 'pools/events/'
        url = base_url + '{}/{}/{}'.format(self.pool_address, start_unix, end_unix)
        response = http_browser(Requestor(
            method='GET',
            url=url,
        ))

        if response and response.success:
            if len(response.data) > 0:
                df = pd.DataFrame([d.__dict__ for d in response.data])
                df.sort_values('ordinal', inplace=True)
                AppLog.logger().debug('request success.')
                return df
            else:
                AppLog.logger().info(f'Request no data from {start_unix} to {end_unix}.')
                return pd.DataFrame()
        else:
            AppLog.logger().error(f'Fetch dex data fail, {start_unix} to {end_unix}.')
            return pd.DataFrame()

    def last_block_time(self):

        response = http_browser(Requestor(
            method='GET',
            url=self.api_domain + 'pools/list',
        ))

        if response and response.success:
            return max(node.lastBlockTime for node in response.data)

        else:
            AppLog.logger().error(f'Get last block info fail.')
            return 0
