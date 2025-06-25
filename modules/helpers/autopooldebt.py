import math
from typing import Dict
from modules.helpers import block
import modules.helpers.autopool4626 as Autopool4626

MAX_DEBT_REPORT_AGE_SECONDS = 60 * 60 * 24 # 1 days
def total_assets_time_checked(
    pool_state: Dict,
    fixed_parameters: Dict,
    purpose: str
) -> int:
    debt_report_queue = pool_state.get('debtReportQueue', [])
    destination_info = fixed_parameters.get('destinationInfo', {})
    recalculated_total_assets = 0

    for dest_vault in debt_report_queue:
        last_report = destination_info[dest_vault].get('lastReport', 0)
        if last_report + MAX_DEBT_REPORT_AGE_SECONDS > block.timestamp:
            break
        
        # currentShares is destVault.balanceOf(address(this)) where `this` is the autopool contract
        current_shares = destination_info[dest_vault].get('currentShares', 0)
        stale_debt = 0
        extreme_price = 0

        if purpose == 'deposit':
            extreme_price = destination_info[dest_vault].get('underlyerCeilingPrice', 0)
            owned_shares = destination_info[dest_vault].get('ownedShares', 0)
            stale_debt = destination_info[dest_vault].get('cachedMaxDebtValue', 0) * current_shares // owned_shares
        elif purpose == 'withdraw':
            extreme_price = destination_info[dest_vault].get('underlyerFloorPrice', 0)
            owned_shares = destination_info[dest_vault].get('ownedShares', 0)
            stale_debt = math.ceil(destination_info[dest_vault].get('cachedMinDebtValue', 0) * current_shares / owned_shares)
        else:
            raise Exception(f"Invalid purpose: {purpose}")
        
        new_value = current_shares * extreme_price // destination_info[dest_vault].get('ONE', 1e18)
        
        if purpose == 'deposit' and stale_debt > new_value:
            new_value = stale_debt
        elif purpose == 'withdraw' and stale_debt < new_value:
            new_value = stale_debt
        
        recalculated_total_assets += new_value
        recalculated_total_assets -= stale_debt

    return recalculated_total_assets