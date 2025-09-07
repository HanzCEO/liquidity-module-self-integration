class IsPriceIncreasing:
	def is_price_increasing(self, amount: int, isToken1: bool) -> bool:
		increasing = isToken1 ^ (amount < 0)
		return bool(increasing)