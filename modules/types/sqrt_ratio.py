class SqrtRatio(int):
	MIN_SQRT_RATIO_RAW = 4611797791050542631
	MAX_SQRT_RATIO_RAW = 79227682466138141934206691491

	BIT_MASK = 0xc00000000000000000000000
	MAX_FIXED_VALUE_ROUND_UP = 0x1000000000000000000000000000000000000000000000000 - 0x4000000000000000000000000
	TWO_POW_95 = 0x800000000000000000000000
	TWO_POW_94 = 0x400000000000000000000000
	TWO_POW_62 = 0x4000000000000000
	TWO_POW_62_MINUS_ONE = 0x3fffffffffffffff

	def to_fixed(self) -> int:
		shift = 2 + ((self & self.BIT_MASK) >> 89)
		result = (self & ~self.BIT_MASK) << shift
		return result
	
	@staticmethod
	def to_sqrt_ratio(sqrt_ratio: int, round_up: bool):
		r = SqrtRatio(0)

		addend = int(round_up) * 0x3

		# lt 2**96 after rounding up
		if sqrt_ratio < 0x1000000000000000000000000 - addend:
			r = (sqrt_ratio + addend) >> 2
		else:
			# 2**34 - 1
			addend = int(round_up) * 0x3ffffffff
			# lt 2**128 after rounding up
			if sqrt_ratio < 0x100000000000000000000000000000000 - addend:
				r = SqrtRatio.TWO_POW_94 | ((sqrt_ratio + addend) >> 34)
			else:
				# 2**98 - 1
				addend = round_up * 0x3ffffffffffffffffffffffff
				if sqrt_ratio < 0x1000000000000000000000000000000000000000000000000 - addend:
					r = SqrtRatio.BIT_MASK | ((sqrt_ratio + addend) >> 98)
				else:
					raise ValueError("types/sqrtRatio.sol: ValueOverflowsSqrtRatioContainer")
		
		return r
	
	def is_valid(self) -> bool:
		left = self & ~self.BIT_MASK > self.TWO_POW_62_MINUS_ONE
		right = ((self < self.MIN_SQRT_RATIO_RAW) == 0) & ((self > self.MAX_SQRT_RATIO_RAW) == 0)
		return left & right