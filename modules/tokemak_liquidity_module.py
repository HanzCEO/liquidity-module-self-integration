from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal
import time, math

class TokemakLiquidityModule(LiquidityModule):
    def _is_stale(self, pool_state: Dict) -> bool:
        TIMEOUT = 60 * 60 * 24
        oldest_debt_reporting = pool_state.get("oldestDebtReporting", 0)
        return int(time.time()) - oldest_debt_reporting >= TIMEOUT

    def _convert_to_shares(
        self,
        pool_state: Dict,
        assets: int
    ) -> int:
        total_supply = pool_state.get('totalSupply', 0)
        total_assets = pool_state.get('totalAssets', 0)
        decimal_offset = 0
        offset = 10 ** decimal_offset

        return math.floor(assets * (total_supply + offset) / (total_assets + 1))

    def _convert_to_assets(
        self,
        pool_state: Dict,
        shares: int
    ) -> int:
        total_supply = pool_state.get('totalSupply', 0)
        total_assets = pool_state.get('totalAssets', 0)
        decimal_offset = 0
        offset = 10 ** decimal_offset

        return math.floor(shares * (total_assets + 1) / (total_supply + offset))
    
    def get_amount_out(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        # Implement logic to calculate output amount given input amount
        pass

    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        # Implement logic to calculate required input amount given output amount
        pass

    def get_apy(
        self, 
        pool_state: Dict,
        underlying_amount:int,
        underlying_token:Token, 
        pool_tokens: Dict[str, Token]
    ) -> int:
        # Implement APY calculation logic
        pass

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
    ) -> int:
        # Implement TVL calculation logic
        pass