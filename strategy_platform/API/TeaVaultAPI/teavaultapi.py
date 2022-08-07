import logging
from dataclasses import dataclass
from httpbrowser import http_browser, Requestor
from datetime import datetime, timedelta
import time
from logger import AppLog, create_logger
import configsettings as cs
from utildomain import TokenSettings


@dataclass
class TeaVaultConnector:
    base_url: str
    tea_vault_address: str
    api_key: str
    config_settings: cs.ConfigSettings

    def api_header(self):
        return {'api-key': self.api_key}


@dataclass
class LP:
    fee: str
    liquidity: str
    tickLower: str
    tickUpper: str
    token0Address: str
    token1Address: str


@dataclass
class TeaVaultAPI:

    connector: TeaVaultConnector

    def __post_init__(self):
        self.connector.config_settings.fee = 500
        self.connector.config_settings.pool_address = '0xc31e54c7a869b9fcbecc14363cf510d1c41fa443'

    def get_vault_positions(self):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/pool/positions',
            headers=self.connector.api_header(),
        ))

    def get_vault_balances(self):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/token',
            headers=self.connector.api_header(),
        ))

    def get_tx_info(self, tx_id):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/trans/{tx_id}',
            headers=self.connector.api_header(),
        ))

    def get_token_amount_in_lp(self, lp_info):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/pool/amount/'
                f'{lp_info.poolAddress}/{lp_info.tickLower}/{lp_info.tickUpper}/{lp_info.liquidity}',
            headers=self.connector.api_header(),
        ))

    def get_pools_address(self, lp_info):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/pool/'
                f'{lp_info.token0Address}/{lp_info.token1Address}/{lp_info.fee}',
            headers=self.connector.api_header(),
        ))

    def get_position_info(self, lp_info):
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/pool/position/'
                f'{lp_info.token0Address}/{lp_info.token1Address}/{lp_info.fee}/'
                f'{lp_info.tickLower}/{lp_info.tickUpper}',
            headers=self.connector.api_header(),
        ))

    def add_liquidity(self, token0, token1, tick_lower, tick_upper, timeout=3):
        tx_info = http_browser(Requestor(
            method='POST',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/liquidity/'
                f'{token0.address}/{token1.address}/{self.connector.config_settings.fee}/'
                f'{tick_lower}/{tick_upper}/'
                f'{token0.long_int_amount()}/{token1.long_int_amount()}'
                f'/0/0/'
                f'{self.unix_utc_with_expired(timeout)}',
            headers=self.connector.api_header(),
        ))
        return self.waiting_to_confirmed('Add liquidity', tx_info, timeout)

    def remove_liquidity(self, lp_info, timeout=3):
        tx_info = http_browser(Requestor(
            method='DELETE',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/liquidity/'
                f'{lp_info.token0Address}/{lp_info.token1Address}/{lp_info.fee}/'
                f'{lp_info.tickLower}/{lp_info.tickUpper}/{lp_info.liquidity}/0/0/'
                f'{self.unix_utc_with_expired(timeout)}',
            headers=self.connector.api_header(),
        ))
        return self.waiting_to_confirmed('Remove', tx_info, timeout)

    def collect_liquidity(self, lp_info, timeout=3):
        tx_info = http_browser(Requestor(
            method='POST',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/collect/'
                f'{lp_info.token0Address}/{lp_info.token1Address}/{self.connector.config_settings.fee}/'
                f'{lp_info.tickLower}/{lp_info.tickUpper}/{int(1e28)}/{int(1e28)}',
            headers=self.connector.api_header(),
        ))
        return self.waiting_to_confirmed('Collect', tx_info, timeout)

    def swap_with_input(self, token_in, token_out, timeout=3):
        AppLog.logger().info(f'Swap token: {token_in.name}, amount: {token_in.amount} for token: {token_out.name}.')

        tx_info = http_browser(Requestor(
            method='POST',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/swap/input_single/'
                f'{token_in.address}/{token_out.address}/{self.connector.config_settings.fee}/'
                f'{self.unix_utc_with_expired(timeout)}/'
                f'{token_in.long_int_amount()}/0/0',
            headers=self.connector.api_header(),
        ))
        return self.waiting_to_confirmed('Swap', tx_info, timeout)

    def get_vault_logs(self, start_time, end_time):
        unix_start_time = int(time.mktime(start_time.timetuple()))
        unix_end_time = int(time.mktime(end_time.timetuple()))
        return http_browser(Requestor(
            method='GET',
            url=f'{self.connector.base_url}/{self.connector.tea_vault_address}/log/'
                f'{unix_start_time}/{unix_end_time}',
            headers=self.connector.api_header(),
        ))

    def waiting_to_confirmed(self, action, tx_info, timeout):
        if tx_info and self.is_tx_confirmed(tx_info.TxID, timeout):
            AppLog.logger().info(f'{action} success.')
            return True
        else:
            AppLog.logger().error(f'{action} fail!')
            return False

    def is_tx_confirmed(self, tx_id, time_out):
        check_expired_time = datetime.now() + timedelta(minutes=time_out)
        while True:
            result = self.get_tx_info(tx_id)
            if result and not result.isPending and \
                    result.receipt and result.receipt.status and result.receipt.status == 'Success':
                AppLog.logger().debug(f'Confirmed tx_id: {tx_id}')
                return True
            elif datetime.now() < check_expired_time:
                AppLog.logger().debug(f'Waiting to confirm tx_id: {tx_id}')
                time.sleep(2)
            else:
                AppLog.logger().error(f'Time out tx_id: {tx_id}')
                return False

    @staticmethod
    def unix_utc_with_expired(timeout):
        return int(time.mktime((datetime.now() + timedelta(minutes=timeout)).timetuple()))

    def unit_test(self):
        # obj = self.get_vault_positions()
        obj6 = self.get_vault_logs(datetime(2022, 4, 15), datetime.now())
        obj3 = self.get_tx_info('0x4d44a34d942409cd2e635d261dea1dd0530516c21afffaf81949a66d49ac25f9')
        # obj3 = get_tx_info(tea_vault_connector, '0xe885ada287475518204877ca74cbede1213403ffec1bd4b25e7f7eb16097d0bf')
        account_bal = self.get_vault_balances()
        # obj5 = get_position_info(tea_vault_connector, next(iter(obj.positions), None))

        token0 = TokenSettings(
            name=account_bal.tokens[0].name,
            address=account_bal.tokens[0].address,
            decimals=account_bal.tokens[0].decimal,
            amount=50086 / 1e18
        )

        token1 = TokenSettings(
            name=account_bal.tokens[1].name,
            address=account_bal.tokens[1].address,
            decimals=account_bal.tokens[1].decimal,
            amount=10 / 1e6,
        )

        # obj7 = self.swap_with_input(token0, token1, 100)
        # balance_after_obj7 = self.get_vault_balances()

        self.add_liquidity(
            token0,
            token1,
            -198060,
            -185160)

        position_after_readd = self.get_vault_positions()

        self.remove_liquidity(next(iter(position_after_readd.positions)))
        self.collect_liquidity(next(iter(position_after_readd.positions)))
        position_after_remove = self.get_vault_positions()

        obj4 = self.get_pools_address(next(iter(obj.positions), None))
        a = ''
