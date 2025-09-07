from modules.libraries.solady.fixed_point_math import FixedPointMathLib
from modules.types.sqrt_ratio import SqrtRatio


class SqrtRatioMath:
	UINT256_MAX = (1 << 256) - 1
	UINT96_MAX = (1 << 96) - 1
	UINT192_MAX = (1 << 192) - 1

	# function nextSqrtRatioFromAmount0(SqrtRatio _sqrtRatio, uint128 liquidity, int128 amount)
	def next_sqrt_ratio_from_amount0(self, _sqrt_ratio: SqrtRatio, liquidity: int, amount: int) -> SqrtRatio:
		if amount == 0:
			return _sqrt_ratio
		if liquidity == 0:
			raise ValueError("math/sqrtRatio.sol: ZeroLiquidityNextSqrtRatioFromAmount0")
		
		sqrt_ratio = _sqrt_ratio.to_fixed()

		liquidity_x128 = liquidity << 128
		amount_abs = FixedPointMathLib.abs(amount)

		if amount < 0:
			if amount_abs > self.UINT256_MAX / sqrt_ratio:
				return SqrtRatio(self.UINT96_MAX)
			
			product = sqrt_ratio * amount_abs

			if product >= liquidity_x128:
				return SqrtRatio(self.UINT96_MAX)
			
			denominator = liquidity_x128 - product

			result_fixed = FixedPointMathLib.full_mul_div_up(liquidity_x128, sqrt_ratio, denominator)

			if result_fixed > SqrtRatio.MAX_FIXED_VALUE_ROUND_UP:
				return SqrtRatio(self.UINT96_MAX)
			
			sqrt_ratio_next = SqrtRatio.to_sqrt_ratio(result_fixed, True)
		else:
			denominator = 0
			
			denominator_p1 = liquidity_x128 // sqrt_ratio
			denominator = denominator_p1 + amount_abs

			sqrt_ratio_next = SqrtRatio.to_sqrt_ratio(FixedPointMathLib.div_up(liquidity_x128, denominator), True)
		
		return sqrt_ratio_next
	
	def next_sqrt_ratio_from_amount1(self, _sqrt_ratio: SqrtRatio, liquidity: int, amount: int) -> SqrtRatio:
		if amount == 0:
			return _sqrt_ratio
		if liquidity == 0:
			raise ValueError("math/sqrtRatio.sol: ZeroLiquidityNextSqrtRatioFromAmount1")
		
		sqrt_ratio = _sqrt_ratio.to_fixed()

		shifted_amount_abs = FixedPointMathLib.abs(amount) << 128
		quotient = shifted_amount_abs / liquidity

		if amount < 0:
			if quotient >= sqrt_ratio:
				# Underflow => return 0
				return SqrtRatio(0)

			sqrt_ratio_next_fixed = sqrt_ratio - quotient

			# subtraction of 1 is safe because sqrtRatio > quotient => sqrtRatio - quotient >= 1
			sqrt_ratio_next_fixed = sqrt_ratio_next_fixed - int(bool(shifted_amount_abs % liquidity))

			sqrt_ratio_next = SqrtRatio.to_sqrt_ratio(sqrt_ratio_next_fixed, False)
		else:
			_sum = sqrt_ratio + quotient
			if _sum < sqrt_ratio or _sum > self.UINT192_MAX:
				return SqrtRatio(self.UINT96_MAX)
			sqrt_ratio_next = SqrtRatio.to_sqrt_ratio(_sum, False)
		
		return sqrt_ratio_next
