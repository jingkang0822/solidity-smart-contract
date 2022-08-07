import os
import enumerator
import utildomain
from dataclasses import dataclass
from datetime import datetime
import feeapi
import utildomain as ud
from environmentvariable import EnvironmentVariable
import pytz


@dataclass
class ConfigSettings:
    chain: enumerator.Chains
    dex: enumerator.DEX
    trading_mode: enumerator.TradingMode
    data_mode: utildomain.DataSettings
    from_dt: datetime
    to_dt: datetime = datetime.now()
    trading_account: enumerator.TradingAccount = None
    token_0: utildomain.TokenSettings = None
    token_1: utildomain.TokenSettings = None
    base_token: utildomain.TokenSettings = None
    quote_token: utildomain.TokenSettings = None
    pool_address: str = None
    fee: int = 0
    tick_spacing: int = None
    is_last_bar_on_chart: bool = False
    fee_api_domain: str = 'http://office.teahouse.finance:8181'
    environment_variable: EnvironmentVariable = None
    api_connector: feeapi.simulator_api = None
    report_folder: str = None
    simulation_detail: enumerator.SimulationDetail = enumerator.SimulationDetail.K_BAR

    def __post_init__(self):

        self.base_token = self.token_0

        if self.pool_address is not None:
            self.api_connector = feeapi.simulator_api(
                network=self.chain.value,
                base_url=self.fee_api_domain,
                pool_address=self.pool_address
            )

            pool_info = self.api_connector.get_pool_info(self)['data']

            self.tick_spacing = pool_info['tick_spacing']
            self.fee = int(pool_info['fee'])
            self.token_0 = ud.TokenSettings(
                pool_info['token0_symbol'],
                pool_info['token0_address'],
                pool_info['token0_decimals']
            )
            self.token_1 = ud.TokenSettings(
                pool_info['token1_symbol'],
                pool_info['token1_address'],
                pool_info['token1_decimals']
            )

        self.from_dt = pytz.utc.localize(self.from_dt)
        self.to_dt = pytz.utc.localize(self.to_dt)

        if self.trading_mode == enumerator.TradingMode.LIVE:
            self.environment_variable = EnvironmentVariable()
            self.to_dt = ud.get_last_k_bar_close_by_initial(self.from_dt, self.get_k_bar_interval())

    def set_token_initial_amount(self, token_name, amount):
        if self.token_0.name == token_name:
            self.token_0.amount = amount

        if self.token_1.name == token_name:
            self.token_1.amount = amount

    def set_token_base(self, token_name):
        if self.token_0.name == token_name:
            self.base_token = self.token_0
            self.quote_token = self.token_1

        if self.token_1.name == token_name:
            self.base_token = self.token_1
            self.quote_token = self.token_0

    def token_ten_base(self):
        return self.token_0.decimals - self.token_1.decimals

    def token_reverse(self):
        if self.token_0 == self.base_token:
            return True
        else:
            return False

    def set_report_path(self, strategy_name):
        date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_folder = os.path.join(
            os.getcwd(),
            'report',
            self.chain.value,
            strategy_name,
            self.get_token_pair_name(),
            date_time
        )
        ud.folder_exists_or_create(self.report_folder)

    def get_token_pair_name(self):
        token_pair = [self.token_0.name, self.token_1.name]
        token_pair.sort()
        return ''.join(token_pair)

    def get_k_bar_interval(self):
        return int(self.data_mode.kbars_interval.total_seconds() / 60)

    def ticks_storage_key(self):
        return f'{self.chain}/{self.pool_address}'
