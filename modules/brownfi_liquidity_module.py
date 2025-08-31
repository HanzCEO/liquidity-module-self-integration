from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class BrownFiLiquidityModule(LiquidityModule):
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
        token0_amount = int(pool_state.get('token0_balance'))
        token1_amount = int(pool_state.get('token1_balance'))
        token0_address = fixed_parameters.get('token0_address')
        token1_address = fixed_parameters.get('token1_address')

        rprice0 = pool_tokens[token0_address].reference_price
        rprice1 = pool_tokens[token1_address].reference_price

        tvl0 = token0_amount * rprice0
        tvl0 //= 10 ** pool_tokens[token0_address].decimals
        
        tvl1 = token1_amount * rprice1
        tvl1 //= 10 ** pool_tokens[token1_address].decimals

        tvl = tvl0 + tvl1

        return int(tvl)