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

timestamp = int(time.time())
pool_state = {'oldestDebtReporting': 1753279643, 'totalSupply': 12097636560995038075600, 'assetBreakdown': {'totalIdle': 1652493105064192344, 'totalDebt': 12633930090626855524705, 'totalDebtMin': 12633261988560572550038, 'totalDebtMax': 12634598192693138499366}, 'previousAssetBreakdown': {'totalIdle': 1.3219944840513539e+18, 'totalDebt': 1.0107144072501484e+22, 'totalDebtMin': 1.0106609590848459e+22, 'totalDebtMax': 1.010767855415451e+22}, 'previousTotalSupply': 9.67810924879603e+21, 'days': 5, 'paused': False, 'shutdown': False, 'profitUnlockSettings': {'unlockPeriodInSeconds': 86400, 'fullProfitUnlockTime': 1753211087, 'lastProfitUnlockTime': 1753193243, 'profitUnlockRate': 0}, 'debtReportQueue': ['0x4142e3a17391676c66ddf1285e43889f168ee237', '0x5c6aeb9ef0d5bba4e6691f381003503fd0d45126', '0x3f55eedde51504e6ed0ec30e8289b4da11edb7f9', '0xba1462f43c6f60ebd1c62735c94e428ad073e01a', '0xe4433d00cf48bfe0c672d9949f2cd2c008bffc04', '0x87e25ffe5c3a2720cd43f5eb8ec41ac0ce699d07', '0x2c7120dccf1c14a37a26a4955475d45d34a3d7e7', '0x40219bbda953ca811d2d0168dc806a96b84791d9', '0x43d99d04985ef2231f7d9b5d9111d2189d9fd971', '0x2e0e2ab6505a1182367dfb1e3c66648bf3eea020', '0x1ea622fa030e4a78f4cc2f305dd3c08da3f08573', '0xc4eb861e7b66f593482a3d7e8adc314f6eeda30b'], 'destinationInfo': {'0xc4eb861e7b66f593482a3d7e8adc314f6eeda30b': {'lastReport': 1753283051, 'ownedShares': 246652204388403049580, 'cachedMaxDebtValue': 247054943475103104092, 'cachedMinDebtValue': 246941427841461743502, 'currentShares': 246652204388403049580, 'underlyerCeilingPrice': 1004034438255158196, 'underlyerFloorPrice': 1000103304120083962, 'ONE': 1000000000000000000}, '0x1ea622fa030e4a78f4cc2f305dd3c08da3f08573': {'lastReport': 1753283051, 'ownedShares': 847482750577982637014, 'cachedMaxDebtValue': 883922561135862358313, 'cachedMinDebtValue': 883358708448783427003, 'currentShares': 847482750577982637014, 'underlyerCeilingPrice': 1052539238817096423, 'underlyerFloorPrice': 991087225568835223, 'ONE': 1000000000000000000}, '0x2e0e2ab6505a1182367dfb1e3c66648bf3eea020': {'lastReport': 1753279643, 'ownedShares': 147620009692798370400, 'cachedMaxDebtValue': 150192257530904527365, 'cachedMinDebtValue': 150189058270356713019, 'currentShares': 147620009692798370400, 'underlyerCeilingPrice': 1017964862588434345, 'underlyerFloorPrice': 1016861032191715782, 'ONE': 1000000000000000000}, '0xba1462f43c6f60ebd1c62735c94e428ad073e01a': {'lastReport': 1753279643, 'ownedShares': 1053243607588726266454, 'cachedMaxDebtValue': 1053265943171028364421, 'cachedMinDebtValue': 1052969848487158796695, 'currentShares': 1053243607588726266454, 'underlyerCeilingPrice': 1002492535222704993, 'underlyerFloorPrice': 998567438159082596, 'ONE': 1000000000000000000}, '0xe4433d00cf48bfe0c672d9949f2cd2c008bffc04': {'lastReport': 1753279643, 'ownedShares': 1223170594540261839325, 'cachedMaxDebtValue': 1244484086688031987281, 'cachedMinDebtValue': 1244457577805973905529, 'currentShares': 1223170594540261839325, 'underlyerCeilingPrice': 1017964862588434345, 'underlyerFloorPrice': 1016861032191715782, 'ONE': 1000000000000000000}, '0x5c6aeb9ef0d5bba4e6691f381003503fd0d45126': {'lastReport': 1753279643, 'ownedShares': 2283879268922849226323, 'cachedMaxDebtValue': 2395528425710503251182, 'cachedMinDebtValue': 2395316943252542305907, 'currentShares': 2283879268922849226323, 'underlyerCeilingPrice': 1055105665502911991, 'underlyerFloorPrice': 986762407700314021, 'ONE': 1000000000000000000}, '0x40219bbda953ca811d2d0168dc806a96b84791d9': {'lastReport': 1753279643, 'ownedShares': 71089962883270806, 'cachedMaxDebtValue': 73277900880731666, 'cachedMinDebtValue': 73264697674925578, 'currentShares': 71089962883270806, 'underlyerCeilingPrice': 1071381589735968223, 'underlyerFloorPrice': 1005595311004051758, 'ONE': 1000000000000000000}, '0x3f55eedde51504e6ed0ec30e8289b4da11edb7f9': {'lastReport': 1753279643, 'ownedShares': 769406503278440269192, 'cachedMaxDebtValue': 806613061928247883703, 'cachedMinDebtValue': 806577723462303585068, 'currentShares': 769406503278440269192, 'underlyerCeilingPrice': 1087035717706460883, 'underlyerFloorPrice': 1003054468868113086, 'ONE': 1000000000000000000}, '0x43d99d04985ef2231f7d9b5d9111d2189d9fd971': {'lastReport': 1753279643, 'ownedShares': 204174639972068254010, 'cachedMaxDebtValue': 204178969796092097594, 'cachedMinDebtValue': 204121570895171999139, 'currentShares': 204174639972068254010, 'underlyerCeilingPrice': 1002492535222704993, 'underlyerFloorPrice': 998567425393532982, 'ONE': 1000000000000000000}, '0x9b163e15121816be53f8d5c85fbefd6e6d9bebcd': {'lastReport': 0, 'ownedShares': 0, 'cachedMaxDebtValue': 0, 'cachedMinDebtValue': 0, 'currentShares': 0, 'underlyerCeilingPrice': 1075760534589630501, 'underlyerFloorPrice': 888086344218395128, 'ONE': 1000000000000000000}, '0x4142e3a17391676c66ddf1285e43889f168ee237': {'lastReport': 1753279643, 'ownedShares': 22734366087291238776, 'cachedMaxDebtValue': 23044272343183439053, 'cachedMinDebtValue': 23044214150250174455, 'currentShares': 22734366087291238776, 'underlyerCeilingPrice': 1038633220901719458, 'underlyerFloorPrice': 987977271814166308, 'ONE': 1000000000000000000}, '0x87e25ffe5c3a2720cd43f5eb8ec41ac0ce699d07': {'lastReport': 1753279643, 'ownedShares': 3703821790973124995045, 'cachedMaxDebtValue': 3754310884855275447500, 'cachedMinDebtValue': 3754301404219066877288, 'currentShares': 3703821790973124995045, 'underlyerCeilingPrice': 1038633220901719458, 'underlyerFloorPrice': 987977271814166308, 'ONE': 1000000000000000000}, '0x2c7120dccf1c14a37a26a4955475d45d34a3d7e7': {'lastReport': 1753279643, 'ownedShares': 1603294068336473589648, 'cachedMaxDebtValue': 1871929508158025307217, 'cachedMinDebtValue': 1871910247029828096878, 'currentShares': 1603294068336473589648, 'underlyerCeilingPrice': 1167656092547845115, 'underlyerFloorPrice': 1167552194651527164, 'ONE': 1000000000000000000}}, 'withdrawalQueue': ['0x1ea622fa030e4a78f4cc2f305dd3c08da3f08573', '0x40219bbda953ca811d2d0168dc806a96b84791d9', '0xe4433d00cf48bfe0c672d9949f2cd2c008bffc04', '0xba1462f43c6f60ebd1c62735c94e428ad073e01a', '0x4142e3a17391676c66ddf1285e43889f168ee237', '0x5c6aeb9ef0d5bba4e6691f381003503fd0d45126', '0x3f55eedde51504e6ed0ec30e8289b4da11edb7f9', '0x87e25ffe5c3a2720cd43f5eb8ec41ac0ce699d07', '0x2c7120dccf1c14a37a26a4955475d45d34a3d7e7', '0x43d99d04985ef2231f7d9b5d9111d2189d9fd971', '0x2e0e2ab6505a1182367dfb1e3c66648bf3eea020', '0xc4eb861e7b66f593482a3d7e8adc314f6eeda30b'], 'withdrawalInfo': {}}

# --- get_amount_out ---
def test_get_amount_out_general(tokemak_module, tokens, fixed_parameters):
    input_amount = 500
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], input_amount
    )
    assert isinstance(out, int)
    assert fee is None

def test_get_amount_out_deposit_exact(tokemak_module, tokens, fixed_parameters):
    input_amount = 10e18
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

def test_get_amount_out_redeem_exact(tokemak_module, tokens, fixed_parameters):
    input_amount = 10e18
    total_assets_time_checked = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'withdraw')
    expected = math.floor(
        (input_amount * total_assets_time_checked)
         /
        pool_state["totalSupply"]
    )
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], input_amount
    )
    assert out == expected
    assert fee is None

def test_get_amount_out_stale(tokemak_module, tokens, fixed_parameters):
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert fee is None and out is None

def test_get_amount_out_vault_to_asset(tokemak_module, tokens, fixed_parameters):
    input_amount = 1e18
    asset = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'withdraw')
    expected = (input_amount*asset)//pool_state['totalSupply']
    fee, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], input_amount
    )
    assert out == expected
    assert fee is None

# --- get_amount_in ---
def test_get_amount_in_general(tokemak_module, tokens, fixed_parameters):
    output_amount = 1e18
    fee, inp = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], output_amount
    )
    assert isinstance(inp, int)
    assert fee is None

def test_get_amount_in_exact(tokemak_module, tokens, fixed_parameters):
    output_amount = 1e18
    asset = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    expected = math.ceil(
        (output_amount * asset)
         /
        pool_state['totalSupply']
    )
    fee, inp = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], output_amount
    )
    assert inp == expected
    assert fee is None

def test_get_amount_in_deposit_exact(tokemak_module, tokens, fixed_parameters):
    output_amount = 10e18
    total_assets_time_checked = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
    expected = math.ceil(
        (output_amount * total_assets_time_checked)
         /
        pool_state["totalSupply"]
    )
    fee, inp = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], output_amount
    )
    fee2, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], inp
    )
    assert inp == expected
    assert fee is None
    assert fee2 is None
    assert out == output_amount

def test_get_amount_in_redeem_exact(tokemak_module, tokens, fixed_parameters):
    output_amount = 10e18
    total_assets_time_checked = autopooldebt.total_assets_time_checked(pool_state, fixed_parameters, 'withdraw')
    expected = math.floor(
        (output_amount * pool_state["totalSupply"])
         /
        total_assets_time_checked
    )
    fee, inp = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], output_amount
    )
    fee2, out = tokemak_module.get_amount_out(
        pool_state, fixed_parameters, tokens["0xVAULT"], tokens["0xASSET"], inp
    )
    assert inp == expected
    assert fee is None
    assert fee2 is None
    assert out == output_amount

def test_get_amount_in_stale(tokemak_module, tokens, fixed_parameters):
    fee, inp = tokemak_module.get_amount_in(
        pool_state, fixed_parameters, tokens["0xASSET"], tokens["0xVAULT"], 100
    )
    assert inp is None and fee is None

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