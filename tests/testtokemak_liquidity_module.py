import pytest
from decimal import Decimal
from modules.tokemak_liquidity_module import TokemakLiquidityModule
from templates.liquidity_module import Token
import time

@pytest.fixture
def tokemak_module():
    return TokemakLiquidityModule()

@pytest.fixture
def tokens():
    asset = Token(address="0xASSET", symbol="ASSET", decimals=18, reference_price=Decimal("1.0"))
    vault = Token(address="0xVAULT", symbol="VAULT", decimals=18, reference_price=Decimal("2.0"))
    return {asset.address: asset, vault.address: vault}

@pytest.fixture
def fixed_parameters(tokens):
    return {"asset": tokens["0xASSET"].address, "vaultTokenAddress": tokens["0xVAULT"].address}

# --- get_amount_out ---
def test_get_amount_out_general(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    input_amount = 500
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], input_amount
    )
    assert isinstance(out, int)
    assert fee is None

def test_get_amount_out_exact(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    input_amount = 100
    # output = floor(100 * (1000+1)/(2000+1)) = floor(100*1001/2001)
    expected = (100*1001)//2001
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], input_amount
    )
    assert out == expected
    assert fee is None

def test_get_amount_out_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert fee is None and out is None

def test_get_amount_out_vault_to_asset(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    input_amount = 100
    # output = floor(100 * (2000+1)/(1000+1))
    expected = (100*2001)//1001
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], input_amount
    )
    assert out == expected
    assert fee is None

# --- get_amount_in ---
def test_get_amount_in_general(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    output_amount = 100
    inp, fee = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], output_amount
    )
    assert isinstance(inp, int)
    assert fee is None

def test_get_amount_in_exact(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    output_amount = 100
    # input = floor(100 * (2000+1)/(1000+1))
    expected = (100*2001)//1001
    inp, fee = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], output_amount
    )
    assert inp == expected
    assert fee is None

def test_get_amount_in_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    inp, fee = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert inp is None and fee is None

def test_get_amount_in_vault_to_asset(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time())
    }
    output_amount = 100
    # input = floor(100 * (1000+1)/(2000+1))
    expected = (100*1001)//2001
    inp, fee = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], output_amount
    )
    assert inp == expected
    assert fee is None

# --- get_apy ---
def test_get_apy_zero_days(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "days": 0,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 10000,
            "totalDebtMax": 10000,
            "totalDebtMin": 10000
        },
        "totalSupply": 10000,
        "previousAssetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 10000,
            "totalDebtMax": 10000,
            "totalDebtMin": 10000
        },
        "previousTotalSupply": 10000,
        "oldestDebtReporting": int(time.time())
    }
    apy = tokemak_module.get_apy(pool_state, 1000, tokens["0xASSET"], tokens)
    assert apy == 0

def test_get_apy_exact(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "days": 365,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2*10**18,
            "totalDebtMax": 2*10**18,
            "totalDebtMin": 2*10**18
        },
        "totalSupply": 2*10**18,
        "previousAssetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1*10**18,
            "totalDebtMax": 1*10**18,
            "totalDebtMin": 1*10**18
        },
        "previousTotalSupply": 1*10**18,
        "oldestDebtReporting": int(time.time())
    }
    expected = 666666666666666666
    apy = tokemak_module.get_apy(pool_state, int(1e18), tokens["0xASSET"], tokens)
    # d_apy = (expected / 1e18) / 365
    daily_apy = expected / 1e18 / 365
    compounded_apy = (1 + daily_apy) ** 365 - 1
    apy_bps = int(compounded_apy * 10000)
    assert apy == apy_bps

def test_get_apy_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "days": 1,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2*10**18,
            "totalDebtMax": 2*10**18,
            "totalDebtMin": 2*10**18
        },
        "totalSupply": 2*10**18,
        "previousAssetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1*10**18,
            "totalDebtMax": 1*10**18,
            "totalDebtMin": 1*10**18
        },
        "previousTotalSupply": 1*10**18,
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    apy = tokemak_module.get_apy(pool_state, int(1e18), tokens["0xASSET"], tokens)
    assert apy is None or apy == (None, None)

# --- get_tvl ---
def test_get_tvl_general(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1e18,
            "totalDebtMax": 1e18,
            "totalDebtMin": 1e18
        },
        "oldestDebtReporting": int(time.time())
    }
    tvl = tokemak_module.get_tvl(pool_state, fixed_parameters, tokens)
    assert isinstance(tvl, int)
    assert tvl > 0

def test_get_tvl_exact(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1e18,
            "totalDebtMax": 1e18,
            "totalDebtMin": 1e18
        },
        "oldestDebtReporting": int(time.time())
    }
    tvl = tokemak_module.get_tvl(pool_state, fixed_parameters, tokens)
    assert tvl == 1

def test_get_tvl_no_token(tokemak_module, fixed_parameters):
    pool_state = {
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1e18,
            "totalDebtMax": 1e18,
            "totalDebtMin": 1e18
        },
        "oldestDebtReporting": 0
    }
    tokens = {}  # No token for asset address
    tvl = tokemak_module.get_tvl(pool_state, fixed_parameters, tokens)
    assert tvl == 0

def test_get_amount_out_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert fee is None and out is None

def test_get_amount_in_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "totalSupply": 1000,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2000,
            "totalDebtMax": 2000,
            "totalDebtMin": 2000
        },
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    inp, fee = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert inp is None and fee is None

def test_get_apy_stale(tokemak_module, tokens, fixed_parameters):
    pool_state = {
        "days": 1,
        "assetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 2*10**18,
            "totalDebtMax": 2*10**18,
            "totalDebtMin": 2*10**18
        },
        "totalSupply": 2*10**18,
        "previousAssetBreakdown": {
            "totalIdle": 0,
            "totalDebt": 1*10**18,
            "totalDebtMax": 1*10**18,
            "totalDebtMin": 1*10**18
        },
        "previousTotalSupply": 1*10**18,
        "oldestDebtReporting": int(time.time()) - 60*60*24 - 1
    }
    apy = tokemak_module.get_apy(pool_state, int(1e18), tokens["0xASSET"], tokens)
    assert apy is None or apy == (None, None)