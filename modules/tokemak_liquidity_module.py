from copy import deepcopy
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal
import time, math

class TokemakLiquidityModule(LiquidityModule):
    # https://docs.tokemak.xyz/developer-docs/integrating/checking-for-stale-data
    def _is_stale(self, pool_state: Dict) -> bool:
        TIMEOUT = 60 * 60 * 24
        oldest_debt_reporting = pool_state.get("oldestDebtReporting", 0)
        return int(time.time()) - oldest_debt_reporting >= TIMEOUT
    
    def _get_assets(
        self,
        pool_state: Dict,
        purpose: str
    ) -> int:
        asset_breakdown = pool_state.get('assetBreakdown', {})
        if purpose == 'global':
            return asset_breakdown.get('totalDebt', 0)
        elif purpose == 'deposit':
            return asset_breakdown.get('totalDebtMax', 0)
        elif purpose == 'withdraw':
            return asset_breakdown.get('totalDebtMin', 0)
        return 0

    # https://docs.tokemak.xyz/developer-docs/integrating/4626-compliance
    def _convert_to_shares(
        self,
        pool_state: Dict,
        assets: int
    ) -> int:
        total_supply = pool_state.get('totalSupply', 0)
        total_assets = self._get_assets(pool_state, 'deposit')
        decimal_offset = 0
        offset = 10 ** decimal_offset

        return math.floor(assets * (total_supply + offset) / (total_assets + 1))

    def _convert_to_assets(
        self,
        pool_state: Dict,
        shares: int
    ) -> int:
        total_supply = pool_state.get('totalSupply', 0)
        total_assets = self._get_assets(pool_state, 'withdraw')
        decimal_offset = 0
        offset = 10 ** decimal_offset

        return math.floor(shares * (total_assets + 1) / (total_supply + offset))
    
    # https://docs.tokemak.xyz/developer-docs/integrating/large-withdrawals
    # https://docs.tokemak.xyz/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopilot-contracts-and-systems/autopilot-router
    # https://docs.tokemak.xyz/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopilot-contracts-and-systems/autopools
    def get_amount_out(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        vault_token_address = fixed_parameters.get('vaultTokenAddress')
        output_amount = None
        fee = None

        if self._is_stale(pool_state):
            return None, None

        if output_token.address == vault_token_address:
            output_amount = self._convert_to_shares(pool_state, input_amount)
        elif input_token.address == vault_token_address:
            output_amount = self._convert_to_assets(pool_state, input_amount)
        
        return fee, output_amount

    # TODO: https://basescan.deth.net/address/0xAADf01DD90aE0A6Bb9Eb908294658037096E0404
    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        vault_token_address = fixed_parameters.get('vaultTokenAddress')
        input_amount = None
        fee = None

        if self._is_stale(pool_state):
            return None, None

        if output_token.address == vault_token_address:
            input_amount = self._convert_to_assets(pool_state, output_amount)
        elif input_token.address == vault_token_address:
            input_amount = self._convert_to_shares(pool_state, output_amount)
        
        return input_amount, fee

    def get_apy(
        self, 
        pool_state: Dict,
        underlying_amount:int,
        underlying_token:Token, 
        pool_tokens: Dict[str, Token]
    ) -> int:
        # Quoting from the FAQ:
        # "Autopool LPs earn rewards as the value of the Autopool increases, meaning the value of their share of the underlying pool increases."
        #
        # There's actualy one more product that Tokemak offers, which is the "sTOKE" staking program. But they require special timing for withdrawals

        if self._is_stale(pool_state):
            return None, None

        # Days between states
        days = pool_state.get("days", 0)

        # Previous state        
        previous_state = {
            "assetBreakdown": pool_state.get("previousAssetBreakdown", None),
            "totalSupply": pool_state.get("previousTotalSupply", 0)
        }
        previous_price = self._convert_to_assets(previous_state, 1e18)
        
        # Current state
        aux_pool_state = deepcopy(pool_state)
        
        shares = self._convert_to_shares(aux_pool_state, underlying_amount)
        aux_pool_state["totalSupply"] += shares
        
        currentPrice = self._convert_to_assets(aux_pool_state, 1e18)

        # Validation
        if days == 0 or previous_price == 0:
            return 0
        
        daily_apy = (currentPrice / previous_price) / days
        compounded_apy = (1 + daily_apy) ** 365 - 1
        apy = compounded_apy * 10000

        return int(apy)

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
    ) -> int:
        total_assets = self._get_assets(pool_state, 'global')
        asset_address = fixed_parameters.get('asset')
        pool_token = pool_tokens.get(asset_address)
        
        if not pool_token:
            return 0
        
        tvl = total_assets * pool_token.reference_price
        tvl /= 10 ** pool_token.decimals

        return int(tvl)