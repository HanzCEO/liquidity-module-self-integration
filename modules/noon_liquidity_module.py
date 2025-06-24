from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class MyProtocolLiquidityModule(LiquidityModule):
    def get_amount_out(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        # Only staking is atomic
        pass

    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        # Only staking is atomic
        pass

    def get_apy(
		self, 
		pool_state: Dict, 
		underlying_amount:int,
		underlying_token:Token, 
		pool_tokens: Dict[Token.address, Token]
    ) -> int:
        # 1 USN/sUSN price disrepancy between `days` compounded everyday for 365 days
        pass

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[Token.address, Token]
    ) -> int:
        # USN + sUSN in sUSN contract
        pass