import pytest
from modules.brownfiv2_liquidity_module import BrownFiV2LiquidityModule
from templates.liquidity_module import Token

BERA_PRICE = 2.19 #USD
BERA = Token("0x6969696969696969696969696969696969696969", "BERA", 18, 1e18)
USDC = Token("0x549943e04f40284185054145c6E4e9568C1D3241", "USDC.e", 6, 1*1e18//BERA_PRICE)
LP = Token("0xd57da672354905b9e42df077df77e554dc5fd1cc", "BF-V2", 18, BERA.reference_price + USDC.reference_price)

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
	pool_state = dict(
		reserve0=20486201958,
		reserve1=9898220874360809436015,
		price0=18445232178565270381,
		price1=43337241514915150978,
		k=92233720368547760,
		fee=300000
	)
	pool_state["lambda"] = 46116860184273880
	
	fixed_parameters = dict(
		token0_address=USDC.address,
		token1_address=BERA.address,
		token0_decimals=USDC.decimals,
		token1_decimals=BERA.decimals,
		lp_token_address=LP.address
	)
	input_token = BERA
	output_token = USDC

	return pool_state, fixed_parameters, input_token, output_token

@pytest.fixture
def get_amount_in_fixture():
	pool_state = dict(
		reserve0=20486201958,
		reserve1=9898220874360809436015,
		price0=18445232178565270381,
		price1=43337241514915150978,
		k=92233720368547760,
		fee=300000
	)
	pool_state["lambda"] = 46116860184273880
	
	fixed_parameters = dict(
		token0_address=USDC.address,
		token1_address=BERA.address,
		token0_decimals=USDC.decimals,
		token1_decimals=BERA.decimals,
		lp_token_address=LP.address
	)
	input_token = BERA
	output_token = USDC

	return pool_state, fixed_parameters, input_token, output_token

@pytest.fixture
def get_amount_out_lp_action_fixture():
	pool_state = dict(
		reserve0=20486201958,
		reserve1=9898220874360809436015,
		price0=18445232178565270381,
		price1=43337241514915150978,
		k=92233720368547760,
		fee=300000,

		balance0=20486201958,
		balance1=9898220874360809436015,
		total_supply=29447185821021052375646
	)
	pool_state["lambda"] = 46116860184273880
	
	fixed_parameters = dict(
		token0_address=USDC.address,
		token1_address=BERA.address,
		token0_decimals=USDC.decimals,
		token1_decimals=BERA.decimals,
		lp_token_address=LP.address
	)
	input_token = USDC
	output_token = LP

	return pool_state, fixed_parameters, input_token, output_token

def test_get_tvl(get_tvl_fixture):
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	expected = pool_tokens['0xtoken0'].reference_price + pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected

def test_get_tvl_different_decimal(get_tvl_fixture):
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_parameters, pool_tokens = get_tvl_fixture

	pool_tokens['0xtoken0'].decimals = 10

	expected = pool_tokens['0xtoken0'].reference_price * pool_state['token0_balance'] / 10**10
	expected += pool_tokens['0xtoken1'].reference_price

	tvl = module.get_tvl(pool_state, fixed_parameters, pool_tokens)
	assert type(tvl) is int
	assert tvl == expected

def test_get_amount_out(get_amount_out_fixture):
	# Source of truth: https://berascan.com/address/0x3f0bbeedea5e5f63a14cbda82718d4f25501fbea#readContract
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_paratemers, input_token, output_token = get_amount_out_fixture

	input_amount = 368933087451577728
	expected = 863945

	output_amount, fee = module.get_amount_out(
		pool_state, fixed_paratemers,
		input_token, output_token,
		input_amount
	)

	assert isinstance(output_amount, int)
	assert isinstance(fee, int)
	assert expected == output_amount
	assert fee < input_amount

def test_get_amount_out_mint(get_amount_out_lp_action_fixture):
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_parameters, input_token, output_token = get_amount_out_lp_action_fixture

	input_amount = 100e6 # $100
	expected = 67139450232358313984

	output_amount, fee = module.get_amount_out(
		pool_state, fixed_parameters,
		input_token, output_token,
		input_amount
	)

	assert isinstance(output_amount, int)
	assert isinstance(fee, int)
	assert expected == output_amount
	assert fee < input_amount

def test_get_amount_out_burn(get_amount_out_lp_action_fixture):
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_parameters, input_token, output_token = get_amount_out_lp_action_fixture

	input_amount = 67139450232358313984
	expected = 99556260 # $100 - fee

	input_token, output_token = output_token, input_token

	output_amount, fee = module.get_amount_out(
		pool_state, fixed_parameters,
		input_token, output_token,
		input_amount
	)

	assert isinstance(output_amount, int)
	assert isinstance(fee, int)
	assert expected == output_amount
	assert fee < input_amount

def test_get_amount_in(get_amount_in_fixture):
	# Source of truth: https://berascan.com/address/0x3f0bbeedea5e5f63a14cbda82718d4f25501fbea#readContract
	module = BrownFiV2LiquidityModule()
	pool_state, fixed_paratemers, input_token, output_token = get_amount_in_fixture

	output_amount = 863945
	expected = 368932941208250605

	input_amount, fee = module.get_amount_in(
		pool_state, fixed_paratemers,
		input_token, output_token,
		output_amount
	)

	assert isinstance(input_amount, int)
	assert isinstance(fee, int)
	assert expected == input_amount
	assert fee < input_amount