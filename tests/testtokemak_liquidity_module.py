import math
import pytest
from decimal import Decimal
from modules.helpers import autopooldebt
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
    timestamp = int(time.time())
    pool_state = {'oldestDebtReporting': timestamp, 'totalSupply': 14061228651455925961932, 'assetBreakdown': {'totalIdle': 160439271227535608447, 'totalDebt': 14507109621135756222228, 'totalDebtMin': 14506935100517394651157, 'totalDebtMax': 14507284141754117793293}, 'previousAssetBreakdown': {'totalIdle': 1.283514169820285e+20, 'totalDebt': 1.1605687696908605e+22, 'totalDebtMin': 1.1605548080413916e+22, 'totalDebtMax': 1.1605827313403295e+22}, 'previousTotalSupply': 1.1248982921164741e+22, 'paused': False, 'shutdown': False, 'profitUnlockSettings': {'unlockPeriodInSeconds': 86400, 'fullProfitUnlockTime': 1751136984, 'lastProfitUnlockTime': 1751114903, 'profitUnlockRate': 7720219197693338752773}, 'debtReportQueue': ['0x1ea622fa030e4a78f4cc2f305dd3c08da3f08573', '0x4142e3a17391676c66ddf1285e43889f168ee237', '0xc4eb861e7b66f593482a3d7e8adc314f6eeda30b', '0x40219bbda953ca811d2d0168dc806a96b84791d9', '0x5c6aeb9ef0d5bba4e6691f381003503fd0d45126', '0x3f55eedde51504e6ed0ec30e8289b4da11edb7f9', '0xba1462f43c6f60ebd1c62735c94e428ad073e01a', '0xe4433d00cf48bfe0c672d9949f2cd2c008bffc04', '0x87e25ffe5c3a2720cd43f5eb8ec41ac0ce699d07', '0x3772973f8f399d74488d5cf3276c032e0afc8a6f', '0x2c7120dccf1c14a37a26a4955475d45d34a3d7e7'], 'destinationInfo': {'0xc4eb861e7b66f593482a3d7e8adc314f6eeda30b': {'lastReport': timestamp, 'ownedShares': 732071191862985215449, 'cachedMaxDebtValue': 733903036603012503155, 'cachedMinDebtValue': 733888842311188052794, 'currentShares': 732071191862985215449, 'underlyerCeilingPrice': 1004318697198517987, 'underlyerFloorPrice': 1001542588481717264, 'ONE': 1000000000000000000}, '0x1ea622fa030e4a78f4cc2f305dd3c08da3f08573': {'lastReport': timestamp, 'ownedShares': 1560805145615796715306, 'cachedMaxDebtValue': 1627720288779392940133, 'cachedMinDebtValue': 1627572377490968862503, 'currentShares': 1560805145615796715306, 'underlyerCeilingPrice': 1066313739483679119, 'underlyerFloorPrice': 1003022996950841898, 'ONE': 1000000000000000000}, '0xdfe3fa7027e84f59b266459c567278c79fe86f0c': {'lastReport': timestamp, 'ownedShares': 0, 'cachedMaxDebtValue': 0, 'cachedMinDebtValue': 0, 'currentShares': 0, 'underlyerCeilingPrice': 1100809894418452556, 'underlyerFloorPrice': 969949781427240906, 'ONE': 1000000000000000000}, '0xba1462f43c6f60ebd1c62735c94e428ad073e01a': {'lastReport': timestamp, 'ownedShares': 1053243607588726266454, 'cachedMaxDebtValue': 1054171106913815384759, 'cachedMinDebtValue': 1054156753430128836447, 'currentShares': 1053243607588726266454, 'underlyerCeilingPrice': 1002731301528370984, 'underlyerFloorPrice': 999816534843352816, 'ONE': 1000000000000000000}, '0xe4433d00cf48bfe0c672d9949f2cd2c008bffc04': {'lastReport': timestamp, 'ownedShares': 2257413756477272038551, 'cachedMaxDebtValue': 2299439242025402033485, 'cachedMinDebtValue': 2299400616884576173347, 'currentShares': 2257413756477272038551, 'underlyerCeilingPrice': 1020227728862502660, 'underlyerFloorPrice': 1017657707407975625, 'ONE': 1000000000000000000}, '0x5c6aeb9ef0d5bba4e6691f381003503fd0d45126': {'lastReport': timestamp, 'ownedShares': 2283879268922849226323, 'cachedMaxDebtValue': 2397889415663627132760, 'cachedMinDebtValue': 2397808173280003072118, 'currentShares': 2283879268922849226323, 'underlyerCeilingPrice': 1074725239394172824, 'underlyerFloorPrice': 1003337150661525303, 'ONE': 1000000000000000000}, '0x40219bbda953ca811d2d0168dc806a96b84791d9': {'lastReport': timestamp, 'ownedShares': 309047697539054158680, 'cachedMaxDebtValue': 318984181242101782195, 'cachedMinDebtValue': 318978190183672125410, 'currentShares': 309047697539054158680, 'underlyerCeilingPrice': 1062071567207274882, 'underlyerFloorPrice': 997814825264085234, 'ONE': 1000000000000000000}, '0x3f55eedde51504e6ed0ec30e8289b4da11edb7f9': {'lastReport': timestamp, 'ownedShares': 769406503278440269192, 'cachedMaxDebtValue': 806355257083193736698, 'cachedMinDebtValue': 806351691105796642131, 'currentShares': 769406503278440269192, 'underlyerCeilingPrice': 1091034385580676667, 'underlyerFloorPrice': 1005387085729279797, 'ONE': 1000000000000000000}, '0x3772973f8f399d74488d5cf3276c032e0afc8a6f': {'lastReport': timestamp, 'ownedShares': 695673772639048074274, 'cachedMaxDebtValue': 697222596059951390937, 'cachedMinDebtValue': 697219123308701472973, 'currentShares': 695673772639048074274, 'underlyerCeilingPrice': 1002391210457243791, 'underlyerFloorPrice': 1002064778242818229, 'ONE': 1000000000000000000}, '0x8e0991e398f9e2f165a2e081f404754d283ae332': {'lastReport': timestamp, 'ownedShares': 0, 'cachedMaxDebtValue': 0, 'cachedMinDebtValue': 0, 'currentShares': 0, 'underlyerCeilingPrice': 1069686956220914190, 'underlyerFloorPrice': 886717361181924136, 'ONE': 1000000000000000000}, '0x4142e3a17391676c66ddf1285e43889f168ee237': {'lastReport': timestamp, 'ownedShares': 22734366087291238776, 'cachedMaxDebtValue': 23010824388254808551, 'cachedMinDebtValue': 23010692734031376864, 'currentShares': 22734366087291238776, 'underlyerCeilingPrice': 1038958548461666174, 'underlyerFloorPrice': 989625921030376874, 'ONE': 1000000000000000000}, '0x87e25ffe5c3a2720cd43f5eb8ec41ac0ce699d07': {'lastReport': timestamp, 'ownedShares': 3703821790973124995045, 'cachedMaxDebtValue': 3748861633978762034780, 'cachedMinDebtValue': 3748840185226694453888, 'currentShares': 3703821790973124995045, 'underlyerCeilingPrice': 1038958548461666174, 'underlyerFloorPrice': 989625921030376874, 'ONE': 1000000000000000000}, '0x2c7120dccf1c14a37a26a4955475d45d34a3d7e7': {'lastReport': timestamp, 'ownedShares': 683535697623514243285, 'cachedMaxDebtValue': 799726559016604045861, 'cachedMinDebtValue': 799708454561633582705, 'currentShares': 683535697623514243285, 'underlyerCeilingPrice': 1169985067052177221, 'underlyerFloorPrice': 1169958040992211026, 'ONE': 1000000000000000000}}}
    fixed_parameters = {'vaultTokenAddress': tokens["0xVAULT"].address, 'asset': tokens["0xASSET"].address}

    input_amount = 100
    total_assets_time_checked = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    expected = math.floor(
        (input_amount * pool_state["totalSupply"])
         /
        total_assets_time_checked
    )
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
    # output = floor(100 * 2000/1000)
    expected = (100*2000)//1000
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
    fee, inp = tokemak_module.get_amount_in(
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
    # input = floor(100 * 2000/1000)
    expected = (100*2000)//1000
    fee, inp = tokemak_module.get_amount_in(
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
    fee, inp = tokemak_module.get_amount_in(
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
    fee, inp = tokemak_module.get_amount_in(
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
    apy = tokemak_module.get_apy(pool_state, int(1e18), tokens["0xASSET"], tokens)
    # Calculate expected APY using the same logic as the implementation
    gain = pool_state["totalSupply"] - pool_state["previousTotalSupply"]
    if pool_state["previousTotalSupply"] == 0 or pool_state["days"] == 0:
        expected_apy_bps = 0
    else:
        daily_apy = (gain * 1e18 // pool_state["previousTotalSupply"]) / pool_state["days"] / 1e18
        compounded_apy = (1 + daily_apy) ** pool_state["days"] - 1
        expected_apy_bps = int(compounded_apy * 10000)
    assert apy == expected_apy_bps

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
    fee, inp = tokemak_module.get_amount_in(
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