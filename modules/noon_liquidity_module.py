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
        # USN total supply
        # ethereum: {
        #     usn: '0xdA67B4284609d2d48e5d10cfAc411572727dc1eD',
        #     susn: '0xE24a3DC889621612422A64E6388927901608B91D',
        # },
        # sophon: {
        #     usn: '0xC1AA99c3881B26901aF70738A7C217dc32536d36',
        #     susn: '0xb87dbe27db932bacaaa96478443b6519d52c5004',
        # },
        # era: {
        #     usn: '0x0469d9d1dE0ee58fA1153ef00836B9BbCb84c0B6',
        #     susn: '0xB6a09d426861c63722Aa0b333a9cE5d5a9B04c4f',
        # }
        
        usn_amount = pool_state.get('totalSupply', 0)
        usn_address = fixed_parameters.get('usn_address')
        price = pool_tokens[usn_address].reference_price

        tvl = usn_amount * price
        tvl /= 10 ** pool_tokens[usn_address].decimals

        return tvl
