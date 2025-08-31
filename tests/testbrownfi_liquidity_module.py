import pytest
from modules.brownfi_liquidity_module import BrownFiLiquidityModule
from templates.liquidity_module import Token

@pytest.fixture
def get_tvl_fixture():
	pool_state = dict(
		token0_balance=1e18,
		token1_balance=1e18
	)
	fixed_parameters = dict(
		token0_address='0xtoken0',
		token1_address='0xtoken1'
	)
	pool_tokens = {
		"0xtoken0": Token('0xtoken0', 'T0', 18, 100),
		"0xtoken1": Token('0xtoken1', 'T1', 18, 200)
	}

	return pool_state, fixed_parameters, pool_tokens

def test_get_tvl(get_tvl_fixture):
	module = BrownFiLiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	expected = pool_tokens['0xtoken0'].reference_price + pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected

def test_get_tvl_different_decimal(get_tvl_fixture):
	module = BrownFiLiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	pool_tokens['0xtoken0'].decimals = 10

	expected = pool_tokens['0xtoken0'].reference_price * pool_state['token0_balance'] / 10**10
	expected += pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected