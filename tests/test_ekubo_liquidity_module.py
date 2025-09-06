import pytest

from templates.liquidity_module import Token
from modules.ekubo_liquidity_module import EkuboLiquidityModule

ETHER_PRICE = 1e18 / 4000 # ETH per USD
USDT = Token('0xdac17f958d2ee523a2206206994597c13d831ec7', 'USDT', 6, 1 * ETHER_PRICE)
USDC = Token('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC', 6, 1 * ETHER_PRICE)

@pytest.fixture
def get_tvl_fixture():
	pool_state = dict()
	fixed_parameters = dict()
	pool_tokens = dict()

	tokens = [USDT, USDC]
	for token in tokens:
		pool_tokens[token.address] = token
	
	for address, token in pool_tokens.items():
		key = address.lower() + '_balance'
		exp = 10**token.decimals
		pool_state[key] = 1_000_000 * exp # $1M USDT/C TVL

	return pool_state, fixed_parameters, pool_tokens


def test_get_tvl(get_tvl_fixture):
	module = EkuboLiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	expected = 1_000_000 * 2 * ETHER_PRICE

	tvl = module.get_tvl(
		pool_state, fixed_parameters,
		pool_tokens
	)

	assert isinstance(tvl, int)
	assert tvl == expected