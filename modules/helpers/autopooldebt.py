from typing import Dict
import modules.helpers.autopool4626 as Autopool4626


def total_assets_time_checked(
    self,
    pool_state: Dict,
    fixed_parameters: Dict,
    purpose: str
) -> int:
    # TODO
    return Autopool4626.get_assets(pool_state, purpose)