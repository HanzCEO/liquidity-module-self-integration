from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class EkuboLiquidityModule(LiquidityModule):
    def get_amount_out(
        self, 
        pool_states: Dict, 
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

    def get_apy(self, pool_state: Dict) -> Decimal:
        # Implement APY calculation logic
        pass

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
    ) -> int:
        tvl = 0

        for address, token in pool_tokens.items():
            token_balance_key = address.lower() + '_balance'
            tvl_token = int(pool_state[token_balance_key])
            tvl_token *= int(token.reference_price)
            tvl_token //= 10 ** token.decimals
            tvl += tvl_token
        
        return tvl