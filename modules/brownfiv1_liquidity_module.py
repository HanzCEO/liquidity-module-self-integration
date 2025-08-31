import math
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class BrownFiV1LiquidityModule(LiquidityModule):
    FEE_DENOMINATOR = 10_000
    Q128 = 1 << 128

    @staticmethod
    def _mul_div(a: int, b: int, denominator: int) -> int:
        """
        Replicates Solidity's FullMath.mulDiv, performing (a * b) / denominator with high precision.
        """
        return (a * b) // denominator

    @staticmethod
    def _mul_div_rounding_up(a: int, b: int, denominator: int) -> int:
        """
        Replicates Solidity's FullMath.mulDivRoundingUp, performing ceil((a * b) / denominator).
        """
        return (a * b + denominator - 1) // denominator

    def sort_tokens(self, token_a, token_b):
        if (token_a == token_b):
            raise Exception("BrownFiV1Library: IDENTICAL_ADDRESSES")
        
        a = int(token_a, 16)
        b = int(token_b, 16)

        token0, token1 = (token_a, token_b) if a < b else (token_b, token_a)
        return token0, token1

    def delta(self, amount_in, reserve_out, kappa, oracle_price, is_sell):
        temp1 = 0
        temp2 = 0

        if is_sell:
            # temp1 = (P * dx - y)^2
            mul_div_val = self._mul_div(oracle_price, amount_in, self.Q128)
            if mul_div_val < reserve_out:
                temp1 = reserve_out - mul_div_val
            else:
                temp1 = mul_div_val - reserve_out
            temp1 *= temp1
        else:
            # temp1 = (P * x - dy)^2
            mul_div_val = self._mul_div(oracle_price, reserve_out, self.Q128)
            if mul_div_val < amount_in:
                temp1 = amount_in - mul_div_val
            else:
                temp1 = mul_div_val - amount_in
            temp1 *= temp1
        
        # temp2 = 2 * P * K * y * dx
        term1 = self._mul_div(oracle_price, amount_in, self.Q128)
        term2 = self._mul_div(kappa, reserve_out, self.Q128)
        temp2 = term1 * term2 * 2
        
        delta_val = temp1 + temp2
        return delta_val
        
    def get_amount_out(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        reserve_in = 0
        reserve_out = 0
        oracle_price = int(pool_state.get('fetch_oracle_price'))
        kappa = int(pool_state.get('kappa'))
        fee_percentage = int(pool_state.get('fee'))
        
        token0, _ = self.sort_tokens(input_token.address, output_token.address)
        zero_for_one = input_token.address == token0

        if zero_for_one:
            reserve_in = int(pool_state.get('reserve0'))
            reserve_out = int(pool_state.get('reserve1'))
        else:
            reserve_in = int(pool_state.get('reserve1'))
            reserve_out = int(pool_state.get('reserve0'))

        if input_amount <= 0:
            raise Exception("BrownFiV1Library: INSUFFICIENT_INPUT_AMOUNT")
        if reserve_in <= 0 or reserve_out <= 0:
            raise Exception("BrownFiV1Library: INSUFFICIENT_LIQUIDITY")
        
        amount_out_before_fee = 0
        if kappa == self.Q128 * 2:
            if zero_for_one:
                # dy = P * y * dx / (P * dx + y)
                numerator = self._mul_div(oracle_price, reserve_out, self.Q128) * input_amount
                denominator = self._mul_div_rounding_up(oracle_price, input_amount, self.Q128) + reserve_out
                amount_out_before_fee = numerator // denominator
            else:
                # dx = (x * dy) / (P * x + dy)
                numerator = input_amount * reserve_out
                denominator = self._mul_div_rounding_up(oracle_price, reserve_out, self.Q128) + input_amount
                amount_out_before_fee = numerator // denominator
        else:
            delta_val = self.delta(input_amount, reserve_out, kappa, oracle_price, zero_for_one)
            sqrt_delta = int(math.sqrt(delta_val))
            
            if zero_for_one:
                # (P * dx + y - sqrt(delta)) / (2 - K)
                numerator = self._mul_div(oracle_price, input_amount, self.Q128) + reserve_out - sqrt_delta
                denominator = self.Q128 * 2 - kappa
                amount_out_before_fee = self._mul_div(numerator, self.Q128, denominator)
            else:
                # (P * x + dy - sqrt(delta)) / (P * (2 - K))
                numerator = self._mul_div(oracle_price, reserve_out, self.Q128) + input_amount - sqrt_delta
                denominator = self._mul_div(oracle_price, (self.Q128 * 2 - kappa), self.Q128)
                amount_out_before_fee = self._mul_div(numerator, self.Q128, denominator)
        
        fee = self._mul_div(amount_out_before_fee, fee_percentage, self.FEE_DENOMINATOR)
        output_amount = self._mul_div(amount_out_before_fee, (self.FEE_DENOMINATOR - fee_percentage), self.FEE_DENOMINATOR)

        return output_amount, fee

    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        oracle_price = int(pool_state.get('fetch_oracle_price'))
        kappa = int(pool_state.get('kappa'))
        fee_percentage = int(pool_state.get('fee'))
        
        token0, _ = self.sort_tokens(input_token.address, output_token.address)
        zero_for_one = input_token.address == token0

        if zero_for_one:
            reserve_in = int(pool_state.get('reserve0'))
            reserve_out = int(pool_state.get('reserve1'))
        else:
            reserve_in = int(pool_state.get('reserve1'))
            reserve_out = int(pool_state.get('reserve0'))

        if output_amount <= 0:
            raise Exception("BrownFiV1Library: INSUFFICIENT_OUTPUT_AMOUNT")
        if reserve_in <= 0 or reserve_out <= 0:
            raise Exception("BrownFiV1Library: INSUFFICIENT_LIQUIDITY")

        # Before fee
        gross_output_amount = self._mul_div_rounding_up(
            output_amount,
            self.FEE_DENOMINATOR,
            self.FEE_DENOMINATOR - fee_percentage
        )

        if gross_output_amount * 10 >= reserve_out * 9:
            raise Exception("BrownFiV1Library: INSUFFICIENT_OUTPUT_AMOUNT")

        # R = (K * dx) / (x - dx)
        r = self._mul_div_rounding_up(
            kappa,
            gross_output_amount,
            reserve_out - gross_output_amount
        )

        q128_x_2 = self.Q128 * 2
        numerator_common = q128_x_2 + r
        avg_price = 0
        
        if zero_for_one:
            # Calculate the required amount of token0 (input) to get token1 (output)
            # avgPrice = (2 + R) / (2 * P)
            avg_price = self._mul_div_rounding_up(numerator_common, self.Q128, oracle_price * 2)
        else:
            # Calculate the required amount of token1 (input) to get token0 (output)
            # avgPrice = P * (2 + R) / 2
            avg_price = self._mul_div_rounding_up(oracle_price, numerator_common, q128_x_2)

        # amountIn = amountOut * avgPrice
        input_amount = self._mul_div_rounding_up(
            gross_output_amount,
            avg_price,
            self.Q128
        )
        
        fee = gross_output_amount - output_amount
        
        return input_amount, fee

    def get_apy(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token],
        input0_amount: int = 0,
        input1_amount: int = 0,
    ) -> int:
        token0_address = fixed_parameters.get('token0_address')
        token1_address = fixed_parameters.get('token1_address')
        token0 = pool_tokens.get(token0_address)
        token1 = pool_tokens.get(token1_address)

        if not token0 or not token1 or token0.reference_price is None or token1.reference_price is None:
            return 0
        
        # dillute to tvl
        pool_state['token0_balance'] += input0_amount
        pool_state['token1_balance'] += input1_amount

        tvl = self.get_tvl(pool_state, fixed_parameters, pool_tokens)

        if tvl == 0:
            return 0

        fee_data = pool_state.get('fees_over_period', {})
        fee_amount0 = fee_data.get('amount0', 0)
        fee_amount1 = fee_data.get('amount1', 0)
        days = fee_data.get('days', 0)

        if days == 0 or (fee_amount0 == 0 and fee_amount1 == 0):
            return 0
            
        fee_value0 = self._mul_div(fee_amount0, token0.reference_price, 10**token0.decimals)
        fee_value1 = self._mul_div(fee_amount1, token1.reference_price, 10**token1.decimals)
        total_fees = fee_value0 + fee_value1
        
        daily_rate_decimal = Decimal(total_fees) / Decimal(tvl) / Decimal(days)
        
        apy_decimal = ((Decimal(1) + daily_rate_decimal) ** 365) - Decimal(1)

        apy_bps = int(apy_decimal * 10_000)
        
        return apy_bps

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