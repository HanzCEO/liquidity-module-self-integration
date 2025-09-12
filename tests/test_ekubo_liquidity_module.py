import pytest
from web3 import Web3

from templates.liquidity_module import Token
from modules.ekubo_liquidity_module import Config, EkuboLiquidityModule, EkuboPoolState, PoolKey

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

def test_pool_state_storage_slot_calculation():
	# source of truth: https://etherscan.io/tx/0xfd375b072ee31becc49f561166ffa0595c4e6982e2ee6e2918491dc1cf80c1a4
	module = EkuboLiquidityModule()

	config = Config(
		"553a2EFc570c9e104942cEC6aC1c18118e54C091",
		1844674407370955,
		100
	)
	pool_key = PoolKey(
		"0000000000000000000000000000000000000000", "2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
		config
	)

	slot = module.calculate_pool_state_storage_slot(pool_key)
	
	assert isinstance(slot, int)
	assert str(slot) == str(18682214692366011081792373943010902514538537518331114227695544810456403192059)

def test_pool_state_class():
	pool_state = EkuboPoolState.from_storage_bytes32("0x0000000000000000000071b8868fdf70fe6f27e340000848d2adf3bdd6f01544")
	raise ValueError(pool_state.liquidity, pool_state.sqrt_ratio, pool_state.tick)