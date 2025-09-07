import math

NOT_0 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
ZERO_BIG = NOT_0 + 1

class FixedPointMathLib:
	"""
	solady lib
	"""

	@staticmethod
	def abs(x: int) -> int:
		return math.abs(x)

	@staticmethod
	def div_up(x: int, d: int) -> int:
		if d == 0:
			raise ValueError("solady/FixedPointMathLib: DivFailed")
		
		return math.ceil(x / d)
	
	@staticmethod
	def full_mul_div(x: int, y: int, d: int) -> int:
		return math.floor((x * y) / d)
	
	@staticmethod
	def full_mul_divn(x: int, y: int, n: int) -> int:
		return math.floor((x * y) / (2**n))
	
	@staticmethod
	def full_mul_div_up(x: int, y: int, d: int) -> int:
		return math.ceil((x * y) / d)
	
	@staticmethod
	def min(x: int, y: int) -> int:
		return min(x, y)
	
	@staticmethod
	def max(x: int, y: int) -> int:
		return max(x, y)