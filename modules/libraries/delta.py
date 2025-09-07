from modules.libraries.solady.fixed_point_math import FixedPointMathLib
from modules.types.sqrt_ratio import SqrtRatio

class Delta:
	UINT128_MAX = (1 << 128) - 1
	def sort_and_convert_to_fixed_sqrt_ratios(self, sqrt_ratio_a: SqrtRatio, sqrt_ratio_b: SqrtRatio) -> tuple[int, int]:
		a_fixed = sqrt_ratio_a.to_fixed()
		b_fixed = sqrt_ratio_b.to_fixed()
		return FixedPointMathLib.min(a_fixed, b_fixed), FixedPointMathLib.max(a_fixed, b_fixed)
	
	def amount0_delta(self, sqrt_ratio_a: SqrtRatio, sqrt_ratio_b: SqrtRatio, liquidity: int, round_up: bool) -> int:
		sqrt_ratio_lower, sqrt_ratio_upper = self.sort_and_convert_to_fixed_sqrt_ratios(sqrt_ratio_a, sqrt_ratio_b)

		if round_up:
			result0 = FixedPointMathLib.full_mul_div_up(
				liquidity << 128, (sqrt_ratio_upper - sqrt_ratio_lower), sqrt_ratio_upper
			)
			result = FixedPointMathLib.div_up(result0, sqrt_ratio_lower)
			
			if result > self.UINT128_MAX:
				raise ValueError("math/delta.sol: Amount0DeltaOverflow")
			
			amount0 = result
		else:
			result0 = FixedPointMathLib.full_mul_div_up(
				liquidity << 128, (sqrt_ratio_upper - sqrt_ratio_lower), sqrt_ratio_upper
			)
			result = result0 / sqrt_ratio_lower
			
			if result > self.UINT128_MAX:
				raise ValueError("math/delta.sol: Amount0DeltaOverflow")
			
			amount0 = result
		return amount0
	
	def amount1_delta(self, sqrt_ratio_a: SqrtRatio, sqrt_ratio_b: SqrtRatio, liquidity: int, round_up: bool) -> int:
		sqrt_ratio_lower, sqrt_ratio_upper = self.sort_and_convert_to_fixed_sqrt_ratios(sqrt_ratio_a, sqrt_ratio_b)

		difference = sqrt_ratio_upper - sqrt_ratio_lower

		if round_up:
			result = FixedPointMathLib.full_mul_divn(difference, liquidity, 128)
			result += int(bool((difference * liquidity) % 0x100000000000000000000000000000000))
			
			if result > self.UINT128_MAX:
				raise ValueError("math/delta.sol: Amount1DeltaOverflow")
			
			amount1 = result
		else:
			result = FixedPointMathLib.full_mul_divn(difference, liquidity, 128)

			if result > self.UINT128_MAX:
				raise ValueError("math/delta.sol: Amount1DeltaOverflow")
			
			amount1 = result
		return amount1