import math
from typing import Dict

import modules.helpers.autopooldebt as AutopoolDebt
import modules.helpers.autopoolfees as AutopoolFees
import modules.helpers.autopool4626 as Autopool4626

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
    total_assets_for_purpose: int = -1,
    is_up: bool = False
) -> int:
    total_supply = pool_state.get('totalSupply', 0)
    total_assets = 0

    if total_assets_for_purpose != -1:
        total_assets = total_assets_for_purpose
    else:
        total_assets = get_assets(pool_state, 'global')

    if total_assets == 0 or total_supply == 0:
        return assets

    if is_up:
        return math.ceil(assets * total_supply / total_assets)
    else:
        return math.floor(assets * total_supply / total_assets)

def convert_to_assets(
    pool_state: Dict,
    shares: int,
    total_assets_for_purpose: int = -1,
    is_up: bool = False
) -> int:
    total_supply = pool_state.get('totalSupply', 0)
    total_assets = 0

    if total_assets_for_purpose != -1:
        total_assets = total_assets_for_purpose
    else:
        total_assets = get_assets(pool_state, 'global')

    if total_supply == 0:
        return shares

    if is_up:
        return math.ceil(shares * total_assets / total_supply)
    else:
        return math.floor(shares * total_assets / total_supply)
    
def max_deposit(
    pool_state: Dict,
    fixed_parameters: Dict
) -> int:
    total_assets = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')

    return Autopool4626.convert_to_assets(
        pool_state,
        Autopool4626.max_mint(pool_state, fixed_parameters),
        total_assets_for_purpose=total_assets,
        is_up=True
    )
    
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
    
    ta = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    if ta == 0:
        return 0
    
    return MAX_UINT112 - ts

def preview_deposit(
    pool_state: Dict,
    fixed_parameters: Dict,
    assets: int
) -> int:
    """
    Derived from AutoPool.deposit(uint256,address)
    Returns the shares users will get if they deposit `assets` amount of underlying asset
    """
    if assets == 0:
        return 0
    
    ta = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    maxDepositAmount = max_deposit(pool_state, fixed_parameters)
    if assets > maxDepositAmount:
        raise Exception(f"ERC4626DepositExceedsMax({assets}, {maxDepositAmount})")
    
    shares = convert_to_shares(pool_state, assets, ta)
    return shares

def preview_mint(
    pool_state: Dict,
    fixed_parameters: Dict,
    shares: int
) -> int:
    """
    Derived from AutoPool.mint(uint256,address)
    Returns the assets needed to mint `shares` amount of shares
    """
    maxMint = max_mint(pool_state, fixed_parameters)
    if shares > maxMint:
        raise Exception(f"ERC4626MintExceedsMax({shares}, {maxMint})")
    
    ta = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    assets = convert_to_assets(pool_state, shares, ta, is_up=True)
    return assets

def preview_withdraw(
    pool_state: Dict,
    fixed_parameters: Dict,
    assets: int
) -> int:
    """
    Derived from AutoPool.withdraw(uint256,address,address)
    Returns the shares needed for users to get `assets` amount of underlying asset
    """
    shares = AutopoolDebt.preview(
        True,
        assets,
        AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'withdraw'),
        "unused, only for readability",
        pool_state['assetBreakdown'],
        pool_state[''] # TODO: Implement withdraw()
    )
    return shares

def preview_redeem(
    pool_state: Dict,
    fixed_paramters: Dict,
    shares: int
) -> int:
    """
    Derived from AutoPool.redeem(uint256,address,address)
    Returns the asset users get from redeeming `shares` amount of shares
    """
    ta = AutopoolDebt.total_assets_time_checked(pool_state, fixed_paramters, 'withdraw')
    # maxShares = max_redeem()
    # redeem will fail if user do not have enough shares, that's what max_redeem check for
    # so we don't need it only for calculations

    possibleAssets = convert_to_assets(pool_state, shares, ta)
    if possibleAssets == 0:
        return 0

    actualAssets, actualShares = AutopoolDebt.redeem(pool_state, possibleAssets, ta) # TODO
    asset = actualAssets
    
    if actualShares > shares:
        raise Exception("Assertion on AutopoolETH.sol:389 failed. User actually need more share.")
    
    return asset