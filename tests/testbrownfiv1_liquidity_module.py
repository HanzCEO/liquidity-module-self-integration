import pytest
from modules.brownfiv1_liquidity_module import BrownFiV1LiquidityModule
from templates.liquidity_module import Token

ETH_PRICE = 4000 # just for simulation: $4k

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

@pytest.fixture
def get_amount_out_fixture():
	# Obtained from: https://berascan.com/address/0x95eeb3B1e77C38bF270E3Db8ad164e7c01A37cb6
	# BERA-USDC.e V1 pool
	pool_state = dict(
		fetch_oracle_price=129443092171794569027180763301664279151315092042041,
		kappa=6805647338418769410938486634724720640,
		fee=15,
		reserve0=883359,
		reserve1=324574876517183227,
		token0_balance=883359,
		token1_balance=324574876517183227
	)

	return pool_state

def test_get_tvl(get_tvl_fixture):
	module = BrownFiV1LiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	expected = pool_tokens['0xtoken0'].reference_price + pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected

def test_get_tvl_different_decimal(get_tvl_fixture):
	module = BrownFiV1LiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	pool_tokens['0xtoken0'].decimals = 10

	expected = pool_tokens['0xtoken0'].reference_price * pool_state['token0_balance'] / 10**10
	expected += pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected

def test_get_amount_out(get_amount_out_fixture):
	module = BrownFiV1LiquidityModule()
	pool_state = get_amount_out_fixture

	input_amount = 368933087451577728
	expected = 831520

	output_amount, fee = module.get_amount_out(
		pool_state, {},
		Token('0x6969696969696969696969696969696969696969', 'BERA', 18, 2.19/ETH_PRICE),
		Token('0x549943e04f40284185054145c6E4e9568C1D3241', 'USDC.e', 6, 1/ETH_PRICE),
		input_amount
	)

	assert type(output_amount) is int
	assert type(fee) is int
	assert output_amount == expected