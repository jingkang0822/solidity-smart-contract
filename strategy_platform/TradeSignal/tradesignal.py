from dataclasses import dataclass
from enum import Enum
import utildomain as ud
import configsettings as cs
from ilCalculator import Amount_CAL


class Liquidity(Enum):
    ADD = 'add'
    REMOVE = 'remove'


@dataclass
class TradeSignal:
    time_stamp: int
    block_number: int
    tick: int
    lower_tick: int = None
    upper_tick: int = None
    event: Liquidity = None
    config_settings: cs.ConfigSettings = None

    def reset_signal(self, k_bar):
        # if the last event is remove liquidity
        if self.event == Liquidity.REMOVE:
            self.lower_tick = None
            self.upper_tick = None

        self.time_stamp = k_bar['timestamp_unix']
        self.block_number = k_bar['block_number']
        self.tick = k_bar['tick']
        self.event = None

    def get_event_value(self):
        return None if self.event is None else self.event.value

    def token_amount_to_mint(self, base_token, quote_token):
        lower_price = ud.tick_to_price(self.config_settings, self.lower_tick)
        upper_price = ud.tick_to_price(self.config_settings, self.upper_tick)
        lower_price, upper_price = ud.ordering_lower_upper(lower_price, upper_price)

        close_price = ud.tick_to_price(self.config_settings, self.tick)
        total_base_token = base_token.amount + quote_token.amount * close_price

        base_token_need_amount, quote_token_need_amount, _ = Amount_CAL(
            P_entry=close_price,
            P_lower=lower_price,
            P_upper=upper_price,
            initial_base_token_amount=total_base_token
        )

        return base_token.new_instance_by_amount(
            base_token_need_amount
        ), quote_token.new_instance_by_amount(
            quote_token_need_amount
        )

    def cal_token_to_swap(self, base_token, quote_token):
        base_token_need, quote_token_need = self.token_amount_to_mint(base_token, quote_token)

        if base_token_need.amount > base_token.amount:
            swap_input_token = quote_token.new_instance_by_amount(
                quote_token.amount - quote_token_need.amount
            )
            swap_output_token = base_token.new_instance_by_amount(
                base_token_need.amount - base_token.amount
            )

        else:
            swap_input_token = base_token.new_instance_by_amount(
                base_token.amount - base_token_need.amount
            )
            swap_output_token = quote_token.new_instance_by_amount(
                quote_token_need.amount - quote_token.amount
            )

        return swap_input_token, swap_output_token
