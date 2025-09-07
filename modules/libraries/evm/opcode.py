def div(x: int, d: int) -> int:
	if d == 0:
		return 0
	return int(x // d)

def mod(x: int, m: int) -> int:
	if m == 0:
		return 0
	return int(x % m)