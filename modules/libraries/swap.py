from modules.libraries.delta import Delta
from modules.libraries.fee import Fee
from modules.libraries.is_price_increasing import IsPriceIncreasing
from modules.libraries.sqrt_ratio import SqrtRatioMath
from modules.types.sqrt_ratio import SqrtRatio

class SwapResult(object):
	consumed_amount: int
	calculated_amount: int
	sqrt_ratio_next: SqrtRatio
	fee_amount: int

	def __init__(self, consumed_amount: int, calculated_amount: int, sqrt_ratio_next: SqrtRatio, fee_amount: int):
		self.consumed_amount = consumed_amount
		self.calculated_amount = calculated_amount
		self.sqrt_ratio_next = sqrt_ratio_next
		self.fee_amount = fee_amount
	
	@staticmethod
	def no_op_swap_result(sqrt_ratio_next: SqrtRatio) -> "SwapResult":
		return SwapResult(
			consumed_amount=0,
			calculated_amount=0,
			sqrt_ratio_next=sqrt_ratio_next,
			fee_amount=0
		)

class EkuboSwap(IsPriceIncreasing, Fee, Delta, SqrtRatioMath):
	def swap_result(
		self,
		sqrt_ratio: SqrtRatio,
		liquidity: int,
		sqrt_ratio_limit: SqrtRatio,
		amount: int,
		is_token1: bool,
		fee: int
	) -> SwapResult:
		if amount == 0 or sqrt_ratio == sqrt_ratio_limit:
			return SwapResult.no_op_swap_result(sqrt_ratio)
		
		increasing = self.is_price_increasing(amount, is_token1)

		if (sqrt_ratio_limit > sqrt_ratio) != increasing:
			raise ValueError("math/swap.sol: SqrtRatioLimitWrongDirection")
		
		if liquidity == 0:
			return SwapResult.no_op_swap_result(sqrt_ratio_limit)
		
		is_exact_out = amount < 0

		if is_exact_out:
			price_impact_amount = amount
		else:
			price_impact_amount = amount - self.compute_fee(amount, fee)
		
		sqrt_ratio_next_from_amount: SqrtRatio
		if is_token1:
			sqrt_ratio_next_from_amount = self.next_sqrt_ratio_from_amount1(sqrt_ratio, liquidity, price_impact_amount)
		else:
			sqrt_ratio_next_from_amount = self.next_sqrt_ratio_from_amount0(sqrt_ratio, liquidity, price_impact_amount)
		
		consumed_amount: int
		calculated_amount: int
		fee_amount: int

		# the amount requires a swapping past the sqrt ratio limit,
		# so we need to compute the result of swapping only to the limit
		if (
			(increasing and sqrt_ratio_next_from_amount > sqrt_ratio_limit) or \
			((not increasing) and sqrt_ratio_next_from_amount < sqrt_ratio_limit)
		):
			specified_amount_delta: int
			calculated_amount_delta: int

			if is_token1:
				specified_amount_delta = self.amount1_delta(sqrt_ratio_limit, sqrt_ratio, liquidity, not is_exact_out)
				calculated_amount_delta = self.amount0_delta(sqrt_ratio_limit, sqrt_ratio, liquidity, is_exact_out)
			else:
				specified_amount_delta = self.amount0_delta(sqrt_ratio_limit, sqrt_ratio, liquidity, not is_exact_out)
				calculated_amount_delta = self.amount1_delta(sqrt_ratio_limit, sqrt_ratio, liquidity, is_exact_out)
			
			if is_exact_out:
				before_fee = self.amount_before_fee(calculated_amount_delta, fee)
				consumed_amount = -specified_amount_delta
				calculated_amount = before_fee
				fee_amount = before_fee - calculated_amount_delta
			else:
				before_fee = self.amount_before_fee(specified_amount_delta, fee)
				consumed_amount = before_fee
				calculated_amount = calculated_amount_delta
				fee_amount = before_fee - specified_amount_delta
			
			return SwapResult(
				consumed_amount,
				calculated_amount,
				sqrt_ratio_next=sqrt_ratio_limit,
				fee_amount=fee_amount
			)
		
		if sqrt_ratio_next_from_amount == sqrt_ratio:
			if not (not is_exact_out):
				raise ValueError("math/swap.sol: assert(!isExactOut)")
			
			return SwapResult(
				consumed_amount=amount,
				calculated_amount=0,
				sqrt_ratio_next=sqrt_ratio,
				fee_amount=amount
			)
		
		# rounds down for calculated == output, up for calculated == input
		calculated_amount_without_fee: int
		if is_token1:
			calculated_amount_without_fee = self.amount0_delta(sqrt_ratio_next_from_amount, sqrt_ratio, liquidity, is_exact_out)
		else:
			calculated_amount_without_fee = self.amount1_delta(sqrt_ratio_next_from_amount, sqrt_ratio, liquidity, is_exact_out)
		
		# add on the fee to calculated amount for exact output
		if is_exact_out:
			including_fee = self.amount_before_fee(calculated_amount_without_fee, fee)
			calculated_amount = including_fee
			fee_amount = including_fee - calculated_amount_without_fee
		else:
			calculated_amount = calculated_amount_without_fee
			fee_amount = amount - price_impact_amount
		
		return SwapResult(
			consumed_amount=amount,
			calculated_amount=calculated_amount,
			sqrt_ratio_next=sqrt_ratio_next_from_amount,
			fee_amount=fee_amount
		)
