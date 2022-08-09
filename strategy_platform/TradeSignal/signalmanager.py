import copy
import queue
from logger import AppLog
from teavaultapi import TeaVaultAPI, TeaVaultConnector
from tradesignal import Liquidity, TradeSignal
from dataclasses import dataclass
import configsettings as cs
import threading
from utildomain import price_to_tick_base, price_to_tick, ordering_lower_upper


@dataclass
class SignalManager:

    config_settings: cs.ConfigSettings
    tea_vault_api: TeaVaultAPI = None
    signal_queue = queue.Queue()

    def __post_init__(self):
        self.tea_vault_api = TeaVaultAPI(
            connector=TeaVaultConnector(
                base_url=self.config_settings.environment_variable.tea_vault_api_url,
                api_key=self.config_settings.environment_variable.api_key,
                tea_vault_address=self.config_settings.environment_variable.tea_vault_address,
                config_settings=copy.deepcopy(self.config_settings)
            )
        )
        self.override_token_address()

        self.listening_thread = threading.Thread(target=self.start_listening)
        self.listening_thread.name = 'Thread-signal'
        self.listening_thread.start()

    def override_token_address(self):
        vault_balances = self.tea_vault_api.get_vault_balances()

        token0_vault = next((x for x in vault_balances.tokens
                             if self.config_settings.token_0.name.upper() in x.symbol.upper()), None)
        token1_vault = next((x for x in vault_balances.tokens
                             if self.config_settings.token_1.name.upper() in x.symbol.upper()), None)

        if token0_vault:
            self.config_settings.token_0.address = token0_vault.address
        if token1_vault:
            self.config_settings.token_1.address = token1_vault.address

        if int(self.config_settings.token_0.address, 16) > int(self.config_settings.token_1.address, 16):
            self.config_settings.token_0, self.config_settings.token_1 = \
                self.config_settings.token_1, self.config_settings.token_0

    def start_listening(self):
        try:
            AppLog.logger().info(f'Signal manager start listening.')
            while True:
                signal_ready = self.signal_queue.get()
                if signal_ready.event:
                    AppLog.logger().info(f'Signal manager received signal: {signal_ready.event.value}')

                    if signal_ready.event == Liquidity.REMOVE:
                        while self.first_of_vault_positions():
                            position = self.first_of_vault_positions()

                            if position:
                                assert self.tea_vault_api.remove_liquidity(position)
                                AppLog.logger().info('Signal manager event remove success.')

                                assert self.tea_vault_api.collect_liquidity(position)
                                AppLog.logger().info('Signal manager event collect success.')
                            else:
                                AppLog.logger().info('There is no position to remove.')

                    elif signal_ready.event == Liquidity.ADD:
                        token0_vault, token1_vault = self.get_vault_balances()
                        token0_vault.amount *= 0.95
                        token1_vault.amount *= 0.95

                        if token0_vault.name == self.config_settings.base_token.name:
                            token_need_to_swap, output_token = \
                                signal_ready.cal_token_to_swap(token0_vault, token1_vault)
                        else:
                            token_need_to_swap, output_token = \
                                signal_ready.cal_token_to_swap(token1_vault, token0_vault)

                        assert token_need_to_swap.amount > 0

                        assert self.tea_vault_api.swap_with_input(token_need_to_swap, output_token)
                        AppLog.logger().info('Signal manager swap success.')

                        token0_vault, token1_vault = self.get_vault_balances()
                        token0_vault.amount *= 0.95
                        token1_vault.amount *= 0.95

                        assert self.tea_vault_api.add_liquidity(
                            token0_vault,
                            token1_vault,
                            signal_ready.lower_tick,
                            signal_ready.upper_tick,
                        )
                        AppLog.logger().info('Signal manager add liquidity success.')

                    else:
                        AppLog.logger().info('Signal manager receive signal not in action list.')

                else:
                    AppLog.logger().info('Signal manager receive signal is None.')

        except Exception as e:
            AppLog.logger().error('Signal manager error, stop listening event, please check!!')
            AppLog.logger().error(e)

    def manual_add_signal(self, close_price, lower_price, upper_price, is_remove_previous):

        lower_tick = price_to_tick_base(self.config_settings, lower_price)
        upper_tick = price_to_tick_base(self.config_settings, upper_price)
        lower_tick, upper_tick = ordering_lower_upper(lower_tick, upper_tick)

        if is_remove_previous:
            self.signal_queue.put(TradeSignal(
                time_stamp=0,
                block_number=0,
                tick=price_to_tick(self.config_settings, close_price),
                event=Liquidity.REMOVE,
                config_settings=self.config_settings,
            ))

        self.signal_queue.put(TradeSignal(
            time_stamp=0,
            block_number=0,
            lower_tick=lower_tick,
            upper_tick=upper_tick,
            tick=price_to_tick(self.config_settings, close_price),
            event=Liquidity.ADD,
            config_settings=self.config_settings,
        ))

    def send_signal(self, signal):
        self.signal_queue.put(signal)

    def first_of_vault_positions(self):
        vault_positions = self.tea_vault_api.get_vault_positions()
        AppLog.logger().info(f'There is {len(vault_positions.positions)} LP in vault.')

        return next(iter(vault_positions.positions), None)

    def get_vault_balances(self):
        balances = self.tea_vault_api.get_vault_balances()

        token0_vault = next((x for x in balances.tokens
                             if x.address.lower() == self.config_settings.token_0.address.lower()), None)
        token1_vault = next((x for x in balances.tokens
                             if x.address.lower() == self.config_settings.token_1.address.lower()), None)

        if token0_vault:
            token0_balance = float(token0_vault.balance) / 10 ** token0_vault.decimal
        else:
            AppLog.logger().warn(f'Can not find {self.config_settings.token_0.name} in vault.')
            token0_balance = 0

        if token1_vault:
            token1_balance = float(token1_vault.balance) / 10 ** token1_vault.decimal
        else:
            AppLog.logger().warn(f'Can not find {self.config_settings.token_1.name} in vault.')
            token1_balance = 0

        token0 = self.config_settings.token_0.new_instance_by_amount(token0_balance)
        token1 = self.config_settings.token_1.new_instance_by_amount(token1_balance)

        AppLog.logger().info(f'Get vault balance success.')
        AppLog.logger().info(f'Vault balance, {token0.name}: {token0.amount}')
        AppLog.logger().info(f'Vault balance, {token1.name}: {token1.amount}')

        return token0, token1
