import math
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class BrownFiV2LiquidityModule(LiquidityModule):
    Q64 = 1 << 64
    PRECISION = 10**8
    DECIMALS = 18

    @staticmethod
    def mul_div(a: int, b: int, c: int) -> int:
        if c == 0:
            raise ValueError("FullMath: division by zero")
        return (a * b) // c
    
    @staticmethod
    def _to_norm(amount: int, decimals: int) -> int:
        if decimals > BrownFiV2LiquidityModule.DECIMALS:
            return amount // (10 ** (decimals - BrownFiV2LiquidityModule.DECIMALS))
        return amount * (10 ** (BrownFiV2LiquidityModule.DECIMALS - decimals))

    @staticmethod
    def _to_raw(amount: int, decimals: int) -> int:
        if decimals > BrownFiV2LiquidityModule.DECIMALS:
            return amount * (10 ** (decimals - BrownFiV2LiquidityModule.DECIMALS))
        return amount // (10 ** (BrownFiV2LiquidityModule.DECIMALS - decimals))

    @staticmethod
    def sort_tokens(addr_a: str, addr_b: str) -> tuple[str, str]:
        return (addr_a, addr_b) if addr_a.lower() < addr_b.lower() else (addr_b, addr_a)

    def _get_skewness_price(
        self,
        token_a: Token,
        token_b: Token,
        reserve_a: int,
        reserve_b: int,
        price_a: int,
        price_b: int,
        lambda_val: int
    ) -> tuple[int, int]:
        if lambda_val == 0:
            return price_a, price_b

        norm_reserve_a = self._to_norm(reserve_a, token_a.decimals)
        norm_reserve_b = self._to_norm(reserve_b, token_b.decimals)

        reserve_a_price = norm_reserve_a * price_a
        reserve_b_price = norm_reserve_b * price_b

        reserve_price_diff = abs(reserve_a_price - reserve_b_price)
        reserve_price_sum = reserve_a_price + reserve_b_price
        
        s = self.mul_div(reserve_price_diff, lambda_val, reserve_price_sum)
        
        q64_plus_s = self.Q64 + s
        q64_minus_s = self.Q64 - s

        if reserve_a_price >= reserve_b_price:
            s_price_a = self.mul_div(price_a, q64_minus_s, self.Q64)
            s_price_b = self.mul_div(price_b, q64_plus_s, self.Q64)
            return s_price_a, s_price_b
        else:
            s_price_a = self.mul_div(price_a, q64_plus_s, self.Q64)
            s_price_b = self.mul_div(price_b, q64_minus_s, self.Q64)
            return s_price_a, s_price_b

    def _calculate_amount_in(
        self,
        output_amount: int,
        reserve_out: int,
        price_in: int,
        price_out: int,
        k: int,
        fee: int,
        input_token: Token,
        output_token: Token
    ) -> int:
        if output_amount * 10 > reserve_out * 8:
            raise ValueError("Output amount exceeds 80% of the reserve")

        normalized_output_amount = self._to_norm(output_amount, output_token.decimals)
        normalized_reserve_out = self._to_norm(reserve_out, output_token.decimals)
        
        if normalized_output_amount > normalized_reserve_out:
            raise ValueError("SafeMath: subtraction overflow")
        
        price_impact_numerator = k * self.Q64
        price_impact_denominator = self.Q64 * (normalized_reserve_out - normalized_output_amount)
        price_impact = self.mul_div(price_impact_numerator, normalized_output_amount, price_impact_denominator)

        inner_term = price_impact + (self.Q64 * 2)
        inner_mul = self.mul_div(price_out, inner_term, price_in)
        amount_in_normalized = self.mul_div(normalized_output_amount, inner_mul, self.Q64 * 2)
        
        amount_in_with_fee = self.mul_div(amount_in_normalized, self.PRECISION + fee, self.PRECISION)

        return self._to_raw(amount_in_with_fee, input_token.decimals)

    def get_amount_out(
        self,
        pool_state: Dict,
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        input_amount: int
    ) -> tuple[int | None, int | None]:
        if input_amount <= 0:
            return None, None

        token0_address, _ = self.sort_tokens(input_token.address, output_token.address)

        if input_token.address == token0_address:
            res_in, res_out = pool_state["reserve0"], pool_state["reserve1"]
            p_in_initial, p_out_initial = pool_state["price0"], pool_state["price1"]
        else:
            res_in, res_out = pool_state["reserve1"], pool_state["reserve0"]
            p_in_initial, p_out_initial = pool_state["price1"], pool_state["price0"]
        
        if res_out <= 0:
            return None, None
        
        lambda_val = pool_state["lambda"]
        (p_in, p_out) = self._get_skewness_price(
            input_token, output_token, res_in, res_out, p_in_initial, p_out_initial, lambda_val
        )

        normalized_input_amount = self._to_norm(input_amount, input_token.decimals)
        normalized_reserve_out = self._to_norm(res_out, output_token.decimals)
        k = pool_state["k"]
        fee_percentage = pool_state["fee"]
        
        amount_in_after_fee = self.mul_div(normalized_input_amount, self.PRECISION, self.PRECISION + fee_percentage)

        if k == 2 * self.Q64:
            numerator = (normalized_reserve_out * amount_in_after_fee) * p_in
            denominator = (p_out * normalized_reserve_out) + (amount_in_after_fee * p_in)
            amount_out_normalized = numerator // denominator
        else:
            numerator_main_term = (p_out * normalized_reserve_out) + (p_in * amount_in_after_fee)

            term1 = self.mul_div(amount_in_after_fee, p_in, self.Q64)
            term2 = self.mul_div(normalized_reserve_out, p_out, self.Q64)
            temp = abs(term1 - term2)
            
            sqrt_left_term = temp * temp

            sqrt_right_term_part1 = self.mul_div(p_in * p_out, k, self.Q64**2)
            sqrt_right_term_part2 = self.mul_div(normalized_reserve_out * amount_in_after_fee, 2, self.Q64)
            sqrt_right_term = sqrt_right_term_part1 * sqrt_right_term_part2

            total_under_sqrt = sqrt_left_term + sqrt_right_term
            sqrt_result = math.isqrt(total_under_sqrt)
            
            numerator_sqrt_term = self.Q64 * sqrt_result
            if numerator_sqrt_term > numerator_main_term:
                raise ValueError("SafeMath: subtraction overflow")
            final_numerator = numerator_main_term - numerator_sqrt_term

            q64_x2 = 2 * self.Q64
            if k > q64_x2:
                raise ValueError("SafeMath: subtraction overflow")
            final_denominator = self.mul_div(p_out, q64_x2 - k, self.Q64)
            
            amount_out_normalized = final_numerator // final_denominator

        final_amt = self._to_raw(amount_out_normalized, output_token.decimals)
        # fee is in input amount
        fee = input_amount - amount_in_after_fee

        try:
            # reverification
            self._calculate_amount_in(final_amt, normalized_reserve_out, p_in, p_out, k, fee_percentage, input_token, output_token)
        except ValueError:
            pass

        return final_amt, fee

    def get_amount_in(
        self,
        pool_state: Dict,
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        if output_amount <= 0:
            return None, None

        token0_address, _ = self.sort_tokens(input_token.address, output_token.address)

        if input_token.address == token0_address:
            res_in, res_out = pool_state["reserve0"], pool_state["reserve1"]
            p_in_initial, p_out_initial = pool_state["price0"], pool_state["price1"]
        else:
            res_in, res_out = pool_state["reserve1"], pool_state["reserve0"]
            p_in_initial, p_out_initial = pool_state["price1"], pool_state["price0"]
        
        if res_out <= 0:
            return None, None

        lambda_val = pool_state["lambda"]
        (p_in, p_out) = self._get_skewness_price(
            input_token, output_token, res_in, res_out, p_in_initial, p_out_initial, lambda_val
        )

        try:
            k = pool_state["k"]
            fee = pool_state["fee"]
            
            final_amt = self._calculate_amount_in(
                output_amount, res_out, p_in, p_out, k, fee, input_token, output_token
            )
            return final_amt, fee
        except ValueError:
            return None, None

    def get_apy(
        self, 
        pool_state: Dict,
        underlying_amount:int,
        underlying_token:Token, 
        pool_tokens: Dict[str, Token]
    ) -> int:
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