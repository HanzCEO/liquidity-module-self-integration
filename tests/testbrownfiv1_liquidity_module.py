import pytest
from modules.brownfiv1_liquidity_module import BrownFiV1LiquidityModule
from templates.liquidity_module import Token

ETH_PRICE = 1e18/4000 # just for simulation: $4k

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
    # https://hermes.pyth.network/docs/#/rest/price_feeds_metadata
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

@pytest.fixture
def get_amount_in_fixture():
    # Obtained from: https://berascan.com/address/0x95eeb3B1e77C38bF270E3Db8ad164e7c01A37cb6
    # BERA-USDC.e V1 pool
    pool_state = dict(
        fetch_oracle_price=131140749449501517724860330728660697551863420087029,
        kappa=6805647338418769410938486634724720640,
        fee=15,
        reserve0=883359,
        reserve1=324574876517183227,
        token0_balance=883359,
        token1_balance=324574876517183227
    )

    return pool_state

@pytest.fixture
def get_apy_fixture():
    bera_address = '0x6969696969696969696969696969696969696969'
    weth_address = '0x4200000000000000000000000000000000000006'

    pool_state = {
        'token0_balance': 1e18,
        'token1_balance': 1e18,
        'fees_over_period': {
            'amount0': 1e18,
            'amount1': 1e18,
            'days': 365
        }
    }
    fixed_parameters = {
        'token0_address': weth_address,
        'token1_address': bera_address
    }
    pool_tokens = {
        bera_address: Token(bera_address, 'BERA', 18, 2.19*ETH_PRICE),
        weth_address: Token(weth_address, 'WETH', 18, 4000.0*ETH_PRICE)
    }
    return pool_state, fixed_parameters, pool_tokens

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
        Token('0x6969696969696969696969696969696969696969', 'BERA', 18, 2.19*ETH_PRICE),
        Token('0x549943e04f40284185054145c6E4e9568C1D3241', 'USDC.e', 6, 1*ETH_PRICE),
        input_amount
    )

    assert type(output_amount) is int
    assert type(fee) is int
    assert output_amount == expected

def test_get_amount_in(get_amount_in_fixture):
    module = BrownFiV1LiquidityModule()
    pool_state = get_amount_in_fixture

    bera_token = Token('0x6969696969696969696969696969696969696969', 'BERA', 18, 2.19*ETH_PRICE)
    usdc_token = Token('0x549943e04f40284185054145c6E4e9568C1D3241', 'USDC.e', 6, 1*ETH_PRICE)

    output_amount = 83152
    expected = 32127363770508483

    input_amount, fee = module.get_amount_in(
        pool_state=pool_state,
        fixed_parameters={},
        input_token=bera_token,
        output_token=usdc_token,
        output_amount=output_amount
    )

    assert isinstance(input_amount, int)
    assert isinstance(fee, int)
    assert input_amount == expected

def test_get_apy(get_apy_fixture):
    module = BrownFiV1LiquidityModule()
    pool_state, fixed_parameters, pool_tokens = get_apy_fixture

    # (( 1+ 1/1/365 ) ** 365) - 1
    #       ^ 100% gain on a year
    # compounded: 1.7145674820219727
    # in BPS: 17145.674820219727
    # but truncated
    expected_apy_bps = 17145

    input0_amount = 1e18
    input1_amount = 1e18

    apy_bps = module.get_apy(
        pool_state=pool_state,
        fixed_parameters=fixed_parameters,
        pool_tokens=pool_tokens
    )

    assert isinstance(apy_bps, int)
    assert apy_bps == expected_apy_bps

def test_get_apy_with_dillution(get_apy_fixture):
    module = BrownFiV1LiquidityModule()
    pool_state, fixed_parameters, pool_tokens = get_apy_fixture

    expected_apy_bps = 6481

    input0_amount = 1e18
    input1_amount = 1e18

    apy_bps = module.get_apy(
        pool_state=pool_state,
        fixed_parameters=fixed_parameters,
        pool_tokens=pool_tokens,
        input0_amount=input0_amount,
        input1_amount=input1_amount
    )

    assert isinstance(apy_bps, int)
    assert apy_bps == expected_apy_bps

def test_get_apy_with_partial_dillution(get_apy_fixture):
    module = BrownFiV1LiquidityModule()
    pool_state, fixed_parameters, pool_tokens = get_apy_fixture

    expected_apy_bps = 9463

    input0_amount = 5e17 # 0.5
    input1_amount = 1e18 # 1.0

    apy_bps = module.get_apy(
        pool_state=pool_state,
        fixed_parameters=fixed_parameters,
        pool_tokens=pool_tokens,
        input0_amount=input0_amount,
        input1_amount=input1_amount
    )

    assert isinstance(apy_bps, int)
    assert apy_bps == expected_apy_bps