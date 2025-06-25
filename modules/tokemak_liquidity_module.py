from copy import deepcopy
from modules.helpers import block
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
import modules.helpers.autopool4626 as Autopool4626
import modules.helpers.autopooldebt as AutopoolDebt

class TokemakLiquidityModule(LiquidityModule):
    # https://docs.tokemak.xyz/developer-docs/integrating/checking-for-stale-data
    def _is_stale(self, pool_state: Dict) -> bool:
        TIMEOUT = 60 * 60 * 24
        oldest_debt_reporting = pool_state.get("oldestDebtReporting", 0)
        return block.timestamp - oldest_debt_reporting >= TIMEOUT
    
    def _convert_to_assets(
        self,
        shares: int,
        total_assets: int,
        total_supply: int,
        is_up: bool = False
    ) -> int:
        return Autopool4626.convert_to_assets(
            {
                'totalSupply': total_supply,
                'assetBreakdown': {'totalDebtMin': total_assets}
            },
            shares,
            is_up
        )

    def _max_deposit(
        self,
        pool_state: Dict,
        fixed_parameters: Dict
    ) -> int:
        total_assets = AutopoolDebt.total_assets_time_checked(pool_state, fixed_parameters, 'deposit')
        total_supply = pool_state.get('totalSupply', 0)

        return self._convert_to_assets(
            Autopool4626.max_mint(pool_state, fixed_parameters),
            total_assets,
            total_supply,
            is_up=True
        )

    # TODO: https://docs.tokemak.xyz/developer-docs/integrating/large-withdrawals
    # https://docs.tokemak.xyz/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopilot-contracts-and-systems/autopilot-router
    # https://docs.tokemak.xyz/developer-docs/contracts-overview/autopool-eth-contracts-overview/autopilot-contracts-and-systems/autopools
    def get_amount_out(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        vault_token_address = fixed_parameters.get('vaultTokenAddress')
        output_amount = None
        fee = None

        if self._is_stale(pool_state):
            return None, None

        if output_token.address == vault_token_address:
            # Deposit mechanism
            max_deposit_amount = self._max_deposit(pool_state, fixed_parameters)
            if input_amount > max_deposit_amount:
                raise Exception(f"Input amount {input_amount} exceeds max deposit amount {max_deposit_amount}")
            
            output_amount = Autopool4626.convert_to_shares(pool_state, input_amount)
        elif input_token.address == vault_token_address:
            # Withdrawal mechanism
            output_amount = Autopool4626.convert_to_assets(pool_state, input_amount)
        
        return fee, output_amount

    # TODO: https://basescan.deth.net/address/0xAADf01DD90aE0A6Bb9Eb908294658037096E0404
    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        vault_token_address = fixed_parameters.get('vaultTokenAddress')
        input_amount = None
        fee = None

        if self._is_stale(pool_state):
            return None, None

        if output_token.address == vault_token_address:
            # Withdrawal mechanism
            input_amount = Autopool4626.convert_to_assets(pool_state, output_amount)
        elif input_token.address == vault_token_address:
            # Deposit mechanism
            input_amount = Autopool4626.convert_to_shares(pool_state, output_amount)

            max_deposit_amount = self._max_deposit(pool_state, fixed_parameters)
            if input_amount > max_deposit_amount:
                raise Exception(f"Input amount {input_amount} exceeds max deposit amount {max_deposit_amount}")
        
        return input_amount, fee

    def get_apy(
        self, 
        pool_state: Dict,
        underlying_amount:int,
        underlying_token:Token, 
        pool_tokens: Dict[str, Token]
    ) -> int:
        # Quoting from the FAQ:
        # "Autopool LPs earn rewards as the value of the Autopool increases, meaning the value of their share of the underlying pool increases."
        #
        # There's actualy one more product that Tokemak offers, which is the "sTOKE" staking program. But they require special timing for withdrawals

        if self._is_stale(pool_state):
            return None, None

        # Days between states
        days = pool_state.get("days", 0)

        # Previous state        
        previous_state = {
            "assetBreakdown": pool_state.get("previousAssetBreakdown", None),
            "totalSupply": pool_state.get("previousTotalSupply", 0)
        }
        
        # Current state
        aux_pool_state = deepcopy(pool_state)
        
        shares = Autopool4626.convert_to_shares(aux_pool_state, underlying_amount)
        aux_pool_state["assetBreakdown"]["totalDebtMin"]
        aux_pool_state["totalSupply"] += shares

        # Price calculation
        previous_price = Autopool4626.convert_to_assets(previous_state, 1e18)
        currentPrice = Autopool4626.convert_to_assets(aux_pool_state, 1e18)

        # Validation
        if days == 0 or previous_price == 0:
            return 0
        
        daily_apy = (currentPrice / previous_price) / days
        compounded_apy = (1 + daily_apy) ** 365 - 1
        apy = compounded_apy * 10000

        return int(apy)

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
    ) -> int:
        total_assets = int(Autopool4626.get_assets(pool_state, 'global'))
        asset_address = fixed_parameters.get('asset')
        pool_token = pool_tokens.get(asset_address)
        
        if not pool_token:
            return 0
        
        tvl = total_assets * pool_token.reference_price
        tvl /= 10 ** pool_token.decimals

        return int(tvl)