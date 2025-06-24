import time
from typing import Dict


def unlocked_shares(
    profit_unlock_settings: Dict,
    pool_state: Dict
) -> int:
    MAX_BPS_PROFIT = 1_000_000_000
    full_time = profit_unlock_settings.get('fullProfitUnlockTime', 0)
    profit_unlock_rate =  profit_unlock_settings.get('profitUnlockRate', 0)
    last_profit_unlock_time =  profit_unlock_settings.get('lastProfitUnlockTime', 0)
    self_balance = pool_state.get('selfBalance', 0) # this.balanceOf(address(this))
    timestamp = int(time.time())

    if full_time > timestamp:
        return profit_unlock_rate * (timestamp - last_profit_unlock_time) / MAX_BPS_PROFIT
    elif full_time != 0:
        return self_balance
    else:
        return 0