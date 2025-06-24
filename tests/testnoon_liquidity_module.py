import pytest
from decimal import Decimal
from modules.noon_liquidity_module import NoonLiquidityModule
from templates.liquidity_module import Token

@pytest.fixture
def noon_module():
    return NoonLiquidityModule()

@pytest.fixture
def tokens():
    usn = Token(address="0xUSN", symbol="USN", decimals=18, reference_price=Decimal("1.0"))
    susn = Token(address="0xSUSN", symbol="sUSN", decimals=18, reference_price=Decimal("1.0"))
    return {usn.address: usn, susn.address: susn}

@pytest.fixture
def fixed_parameters(tokens):
    return {"usn_address": tokens["0xUSN"].address, "susn_address": tokens["0xSUSN"].address}

# --- get_amount_out ---
def test_get_amount_out_general(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    input_amount = 500
    out, fee = noon_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xUSN"], tokens["0xSUSN"], input_amount
    )
    assert isinstance(out, int)
    assert fee is None

def test_get_amount_out_exact(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    input_amount = 100
    # output = floor(100 * (1000+1)/(2000+1)) = floor(100*1001/2001)
    expected = (100*1001)//2001
    out, fee = noon_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xUSN"], tokens["0xSUSN"], input_amount
    )
    assert out == expected
    assert fee is None

def test_get_amount_out_wrong_tokens(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    out, fee = noon_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xSUSN"], tokens["0xUSN"], 100
    )
    assert out is None and fee is None

# --- get_amount_in ---
def test_get_amount_in_general(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    output_amount = 100
    inp, fee = noon_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xUSN"], tokens["0xSUSN"], output_amount
    )
    assert isinstance(inp, int)
    assert fee is None

def test_get_amount_in_exact(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    output_amount = 100
    # input = floor(100 * (2000+1)/(1000+1))
    expected = (100*2001)//1001
    inp, fee = noon_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xUSN"], tokens["0xSUSN"], output_amount
    )
    assert inp == expected
    assert fee is None

def test_get_amount_in_wrong_tokens(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1000, "totalAssets": 2000}
    inp, fee = noon_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xSUSN"], tokens["0xUSN"], 100
    )
    assert inp is None and fee is None

# --- get_apy ---
def test_get_apy_zero_days(noon_module, tokens):
    pool_state = {"days": 0}
    apy = noon_module.get_apy(pool_state, 1000, tokens["0xUSN"], tokens)
    assert apy == 0

def test_get_apy_compound(noon_module, tokens):
    pool_state = {
        "days": 10,
        "prevTotalAssets": 10000,
        "prevTotalSupply": 10000,
        "totalAssets": 12000,
        "totalSupply": 12000,
    }
    # This is a general test, just check int output
    apy = noon_module.get_apy(pool_state, 1000, tokens["0xUSN"], tokens)
    assert isinstance(apy, int)
    assert apy > 0

def test_get_apy_exact(noon_module, tokens):
    pool_state = {
        "days": 1,
        "prevTotalAssets": 1e18,
        "prevTotalSupply": 1e18,
        "totalAssets": 2e18,
        "totalSupply": 2e18,
    }
    apy = noon_module.get_apy(pool_state, 1e18, tokens["0xUSN"], tokens)
    assert apy != 2**365 * 10000 - 1 # Must be dilluted
    assert apy == 502902801166828306432

# --- get_tvl ---
def test_get_tvl_general(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1e18}
    tvl = noon_module.get_tvl(pool_state, fixed_parameters, tokens)
    assert isinstance(tvl, int)
    assert tvl > 0

def test_get_tvl_exact(noon_module, tokens, fixed_parameters):
    pool_state = {"totalSupply": 1e18}
    # price = 1.0, decimals = 18, so tvl = 1e18 * 1.0 / 1e18 = 1.0
    tvl = noon_module.get_tvl(pool_state, fixed_parameters, tokens)
    assert tvl == 1.0
