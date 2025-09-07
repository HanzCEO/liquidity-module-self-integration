class Fee:
	def compute_fee(self, amount: int, fee: int) -> int:
		result = ((amount * fee) + 0xffffffffffffffff) >> 64
		return result