from modules.libraries.evm.opcode import div, mod

class Fee:
	def compute_fee(self, amount: int, fee: int) -> int:
		result = ((amount * fee) + 0xffffffffffffffff) >> 64
		return result
	
	def amount_before_fee(self, after_fee: int, fee: int) -> int:
		v = after_fee << 64
		d = 0x10000000000000000 - fee
		q = div(v, d)
		r = int(bool(mod(v, d))) + q

		if r > (1 << 128) - 1:
			raise ValueError("math/fee.sol: AmountBeforeFeeOverflow")
		
		return r