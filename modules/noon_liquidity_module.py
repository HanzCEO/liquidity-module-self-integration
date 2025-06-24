import math
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class NoonLiquidityModule(LiquidityModule):
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
        usn_address = fixed_parameters.get('usn_address')
        susn_address = fixed_parameters.get('susn_address')

        if input_token.address != usn_address or output_token.address != susn_address:
            return None, None
        
        output_amount = self._convert_to_shares(
            pool_state,
            input_amount
        )
        return output_amount, None

    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        usn_address = fixed_parameters.get('usn_address')
        susn_address = fixed_parameters.get('susn_address')

        if input_token.address != usn_address or output_token.address != susn_address:
            return None, None
        
        input_amount = self._convert_to_assets(
            pool_state,
            output_amount
        )
        return input_amount, None

    def get_apy(
		self, 
		pool_state: Dict,
		underlying_amount:int,
		underlying_token:Token, 
		pool_tokens: Dict[str, Token]
    ) -> int:
        # 1 sUSN/USN price disrepancy between `days` compounded everyday for 365 days
        usn_address = underlying_token.address
        days = pool_state.get('days', 0)
        # Previous state
        previous_total_assets = pool_state.get('prevTotalAssets', 0)
        previous_total_supply = pool_state.get('prevTotalSupply', 0)
        previous_pool_state = {
            'totalAssets': previous_total_assets,
            'totalSupply': previous_total_supply
        }
        # Current state
        current_pool_state = {
            'totalAssets': pool_state.get('totalAssets', 0),
            'totalSupply': pool_state.get('totalSupply', 0)
        }

        if days == 0:
            return 0
        
        # Dillute the current state
        current_pool_state['totalAssets'] += underlying_amount
        current_pool_state['totalSupply'] += self._convert_to_shares(
            current_pool_state,
            underlying_amount
        )

        # Calculate price disrepancy
        previous_price = self._convert_to_shares(
            previous_pool_state,
            underlying_amount
        )

        current_price = self._convert_to_shares(
            current_pool_state,
            underlying_amount
        )

        d_price = previous_price - current_price # lower sUSN/USN price means profit
        daily_apy = d_price / previous_price / days

        compounded_apy = (1 + daily_apy) ** 365 - 1
        apy_bps = compounded_apy * 10000

        return int(apy_bps)

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
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

        usn_amount = int(pool_state.get('totalSupply', 0))
        usn_address = fixed_parameters.get('usn_address')
        price = pool_tokens[usn_address].reference_price

        tvl = usn_amount * price
        tvl /= 10 ** pool_tokens[usn_address].decimals

        return int(tvl)
