import math
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal

class BrownFiV2LiquidityModule(LiquidityModule):
    MINIMUM_LIQUIDITY = 10**3
    Q64 = 1 << 64
    PRECISION = 10**8
    DECIMALS = 18

    @staticmethod
    def mul_div(a: int, b: int, c: int) -> int:
        if c == 0:
            raise ValueError("FullMath: division by zero")
        return (a * b) // c
    
    @staticmethod
    # parseRawToDefaultDecimals
    def _to_norm(amount: int, decimals: int) -> int:
        if decimals > BrownFiV2LiquidityModule.DECIMALS:
            return amount // (10 ** (decimals - BrownFiV2LiquidityModule.DECIMALS))
        return amount * (10 ** (BrownFiV2LiquidityModule.DECIMALS - decimals))

    @staticmethod
    # parseDefaultDecimalsToRaw
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
    
    def _mint(
        self,
        reserve0: int, reserve1: int,
        balance0: int, balance1: int,
        price0: int, price1: int,
        token0: Token, token1: Token,
        total_supply: int
    ) -> int:
        amount0 = balance0 - reserve0
        amount1 = balance1 - reserve1

        parsed_amount0 = self._to_norm(amount0, token0.decimals)
        parsed_amount1 = self._to_norm(amount1, token1.decimals)

        min_value = min(parsed_amount0 * price0, parsed_amount1 * price1)

        if total_supply == 0:
            liquidity = self.mul_div(min_value, 2, self.Q64) - self.MINIMUM_LIQUIDITY
        else:
            parsed_reserve0 = self._to_norm(reserve0, token0.decimals)
            parsed_reserve1 = self._to_norm(reserve1, token1.decimals)
            liquidity = self.mul_div(
                total_supply,
                min_value * 2,
                price0 * parsed_reserve0 + (price1 * parsed_reserve1)
            )
        
        if liquidity <= 0:
            raise Exception("BrownFiV2: INSUFFICIENT_LIQUIDITY_MINTED")
        
        return int(liquidity)
    
    def _burn(
        self,
        balance0: int, balance1: int,
        liquidity: int, total_supply: int
    ) -> tuple[int, int, int, int]:
        amount0 = self.mul_div(liquidity, balance0, total_supply)
        amount1 = self.mul_div(liquidity, balance1, total_supply)

        if amount0 <= 0 or amount1 <= 0:
            raise Exception("BrownFiV2: INSUFFICIENT_LIQUIDITY_BURNED")
        
        new_reserve0 = balance0 - amount0
        new_reserve1 = balance1 - amount1

        return amount0, amount1, new_reserve0, new_reserve1
    
    def _prepare_swap(
        self,
        input_token: Token, output_token: Token,
        token0_address: str,
        reserve0: int, reserve1: int,
        price0: int, price1: int,
        lambda_val: int
    ) -> tuple[int, int, int, int]:
        if input_token.address == token0_address:
            res_in, res_out = reserve0, reserve1
            p_in_initial, p_out_initial = price0, price1
        else:
            res_in, res_out = reserve1, reserve0
            p_in_initial, p_out_initial = price1, price0
        
        if res_out <= 0:
            raise Exception("Prepare swap failed: res_out <= 0")
        
        p_in, p_out = self._get_skewness_price(
            input_token, output_token, res_in, res_out, p_in_initial, p_out_initial, lambda_val
        )

        return res_in, res_out, p_in, p_out
    
    def _get_amount_out(
        self,
        input_token: Token,
        output_token: Token,
        input_amount: int,
        res_out: int,
        p_in: int, p_out: int,
        k: int,
        fee_percentage: int
    ) -> tuple[int | None, int | None]:
        normalized_input_amount = self._to_norm(input_amount, input_token.decimals)
        normalized_reserve_out = self._to_norm(res_out, output_token.decimals)
        
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
            sqrt_result = int(math.sqrt(total_under_sqrt))
            
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
        if fee < 0:
            fee = 0

        try:
            # reverification
            self._calculate_amount_in(final_amt, normalized_reserve_out, p_in, p_out, k, fee_percentage, input_token, output_token)
        except ValueError:
            pass

        return final_amt, fee

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

        token0_address, token1_address = fixed_parameters["token0_address"], fixed_parameters["token1_address"]
        reserve0, reserve1 = pool_state["reserve0"], pool_state["reserve1"]
        price0, price1 = pool_state["price0"], pool_state["price1"]
        lambda_val = pool_state["lambda"]
        k = pool_state["k"]
        fee_percentage = pool_state["fee"]
        token0 = Token(token0_address, "T0", fixed_parameters["token0_decimals"], 0)
        token1 = Token(token1_address, "T1", fixed_parameters["token1_decimals"], 0)

        is_lp_action = 0
        if input_token.address == fixed_parameters["lp_token_address"]:
            is_lp_action = 2 # burn
        elif output_token.address == fixed_parameters["lp_token_address"]:
            is_lp_action = 1 # mint
        
        if is_lp_action == 0:
            # normal swap
            res_in, res_out, p_in, p_out = self._prepare_swap(
                input_token, output_token,
                token0_address,
                reserve0, reserve1,
                price0, price1,
                lambda_val
            )
            output_amount, fee = self._get_amount_out(
                input_token, output_token, input_amount,
                res_out,
                p_in, p_out,
                k, fee_percentage
            )
        elif is_lp_action == 1:
            # mint
            # only load these params when needed
            balance0, balance1 = pool_state["balance0"], pool_state["balance1"]
            total_supply = pool_state["total_supply"]

            if token0.address == input_token.address:
                balance0 += input_amount//2
                # balance out with 50:50 LPing ratio
                res_in, res_out, p_in, p_out = self._prepare_swap(
                    token0, token1,
                    token0_address,
                    reserve0, reserve1,
                    price0, price1,
                    lambda_val
                )
                nb, fee = self._get_amount_out(
                    token0, token1, input_amount//2,
                    res_out,
                    p_in, p_out,
                    k, fee_percentage
                )
                balance1 += nb
            elif token1.address == input_token.address:
                balance1 += input_amount//2
                # balance out with 50:50 LPing ratio
                res_in, res_out, p_in, p_out = self._prepare_swap(
                    token1, token0,
                    token0_address,
                    reserve0, reserve1,
                    price0, price1,
                    lambda_val
                )
                nb, fee = self._get_amount_out(
                    token1, token0, input_amount//2,
                    res_out,
                    p_in, p_out,
                    k, fee_percentage
                )
                balance0 += nb

            output_amount = self._mint(
                reserve0, reserve1,
                balance0, balance1,
                price0, price1,
                token0, token1,
                total_supply
            )
            # We have fee when doing 50:50 LPing ratio
            # because of swap
            # fee = None
        elif is_lp_action == 2:
            # burn
            # only load these params when needed
            balance0, balance1 = pool_state["balance0"], pool_state["balance1"]
            total_supply = pool_state["total_supply"]
            
            output0, output1, new_reserve0, new_reserve1 = self._burn(
                balance0, balance1,
                input_amount,
                total_supply
            )

            # swap into one asset: output_token
            if output_token is token0:
                res_out = new_reserve0
                output_amount = output0

                input_token = token1
                input_amount = output1
            elif output_token is token1:
                res_out = new_reserve1
                output_amount = output1

                input_token = token0
                input_amount = output0

            # there's a swap fee when you burn with this function
            # because you earn 2 tokens. But, now you have to get
            # output_token only, instead.
            res_in, res_out, p_in, p_out = self._prepare_swap(
                input_token, output_token,
                token0_address,
                reserve0, reserve1,
                price0, price1,
                lambda_val
            )
            another_output, fee = self._get_amount_out(
                input_token, output_token, input_amount,
                res_out,
                p_in, p_out,
                k, fee_percentage
            )

            output_amount += another_output
        
        return output_amount, fee

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