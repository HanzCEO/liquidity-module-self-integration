import math
from typing import Dict

import modules.helpers.autopooldebt as AutopoolDebt
import modules.helpers.autopoolfees as AutopoolFees

def get_assets(
    pool_state: Dict,
    purpose: str
) -> int:
    asset_breakdown = pool_state.get('assetBreakdown', {})
    idle_assets = asset_breakdown.get('totalIdle', 0)
    if purpose == 'global':
        return idle_assets + asset_breakdown.get('totalDebt', 0)
    elif purpose == 'deposit':
        return idle_assets + asset_breakdown.get('totalDebtMax', 0)
    elif purpose == 'withdraw':
        return idle_assets + asset_breakdown.get('totalDebtMin', 0)

# https://docs.tokemak.xyz/developer-docs/integrating/4626-compliance
def convert_to_shares(
    pool_state: Dict,
    assets: int,
    is_up: bool = False
) -> int:
    total_supply = pool_state.get('totalSupply', 0)
    total_assets = get_assets(pool_state, 'deposit')
    decimal_offset = 0
    offset = 10 ** decimal_offset

    if is_up:
        return math.ceil(assets * (total_supply + offset) / (total_assets + 1))
    else:
        return math.floor(assets * (total_supply + offset) / (total_assets + 1))

def convert_to_assets(
    pool_state: Dict,
    shares: int,
    is_up: bool = False
) -> int:
    total_supply = pool_state.get('totalSupply', 0)
    total_assets = get_assets(pool_state, 'withdraw')
    decimal_offset = 0
    offset = 10 ** decimal_offset

    if is_up:
        return math.ceil(shares * (total_assets + 1) / (total_supply + offset))
    else:
        return math.floor(shares * (total_assets + 1) / (total_supply + offset))
    
def max_mint(
    pool_state: Dict,
    fixed_parameters: Dict
) -> int:
    MAX_UINT112 = 2 ** 112 - 1
    paused = pool_state.get('paused', False)
    shutdown = pool_state.get('shutdown', False)
    total_supply = pool_state.get('totalSupply', 0)
    profit_unlock_settings = pool_state.get('profitUnlockSettings', {})

    if paused or shutdown:
        return 0
    
    ts = total_supply - AutopoolFees.unlocked_shares(profit_unlock_settings, pool_state)
    if ts == 0:
        return  MAX_UINT112
    if ts > MAX_UINT112:
        return 0
    
    # TODO
    ta = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    if ta == 0:
        return 0
    
    return MAX_UINT112 - ts