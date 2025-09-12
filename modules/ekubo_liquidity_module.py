from hexbytes import HexBytes
from web3 import Web3
from modules.libraries.swap import EkuboSwap
from modules.types.sqrt_ratio import SqrtRatio
from templates.liquidity_module import LiquidityModule, Token
from typing import Dict, Optional
from decimal import Decimal
from eth_abi import encode, abi

class Config:
    # The config is a single 32-byte value.
    _config_bytes: bytes

    def __init__(self, extension_address: str, fee: int, tick_spacing: int):
        extension_int = int(extension_address, 16)

        # c := add(add(shl(96, _extension), shl(32, _fee)), _tickSpacing)
        config_int = (extension_int << 96) | (fee << 32) | tick_spacing

        self._config_bytes = config_int.to_bytes(32, 'big')

    def as_bytes32(self) -> bytes:
        return self._config_bytes

    def as_hex(self) -> str:
        return '0x' + self._config_bytes.hex()


class PoolKey:
    token0: str
    token1: str
    config: Config

    def __init__(self, token0: str, token1: str, config: Config):
        # The PoolKey requires tokens to be sorted.
        if token0.lower() >= token1.lower():
            raise ValueError("TokensMustBeSorted: token0 address must be less than token1 address.")
        
        # Store addresses in checksum format, as expected by ABI encoders.
        self.token0 = Web3.to_checksum_address(token0)
        self.token1 = Web3.to_checksum_address(token1)
        self.config = config

    def to_pool_id(self) -> bytes:
        types = ['address', 'address', 'bytes32']

        values = [self.token0, self.token1, self.config.as_bytes32()]

        encoded_data = encode(types, values)

        return Web3.keccak(encoded_data)

    def to_pool_id_hex(self) -> str:
        return self.to_pool_id().hex()

class EkuboPoolState(object):
    sqrt_ratio: SqrtRatio
    tick: int
    liquidity: int

    def __init__(self, _sqrt_ratio: SqrtRatio, _tick: int, _liquidity: int):
        self.sqrt_ratio = _sqrt_ratio
        self.tick = _tick
        self.liquidity = _liquidity
    
    @staticmethod
    def from_bytes32(bytes32: HexBytes) -> "EkuboPoolState":
        sqrt_ratio, tick, liquidity = abi.decode(('uint96', 'int32', 'uint128'), bytes32)
        return EkuboPoolState(sqrt_ratio, tick, liquidity)

class EkuboCore(EkuboSwap):
    def calculate_pool_state_storage_slot(self, poolkey: PoolKey) -> int:
        # PoolState is 256 bits of data, it is packed into one slot
        state_mapping_base_slot = 2
        final_storage_slot = 0
        
        pool_id = poolkey.to_pool_id()
        base_slot_bytes = state_mapping_base_slot.to_bytes(32, 'big', signed=False)
        final_storage_slot = int.from_bytes(
            Web3.keccak(pool_id + base_slot_bytes),
            'big'
        )
        return final_storage_slot
    
    def fetch_pool_state(self, fixed_parameters: Dict, w3: Web3, poolkey: PoolKey) -> EkuboPoolState:
        core_address = fixed_parameters["core_address"] # 0xe0e0e08a6a4b9dc7bd67bcb7aade5cf48157d444
        storage_position = self.calculate_pool_state_storage_slot(poolkey)
        val = w3.eth.get_storage_at(core_address, storage_position)
        return EkuboPoolState.from_storage_bytes32(val)

class EkuboLiquidityModule(LiquidityModule, EkuboCore):
    def get_amount_out(
        self, 
        pool_states: Dict, 
        fixed_parameters: Dict,
        input_token: Token, 
        output_token: Token,
        input_amount: int, 
    ) -> tuple[int | None, int | None]:
        # Implement logic to calculate output amount given input amount
        pass

    def get_amount_in(
        self, 
        pool_state: Dict, 
        fixed_parameters: Dict,
        input_token: Token,
        output_token: Token,
        output_amount: int
    ) -> tuple[int | None, int | None]:
        # Implement logic to calculate required input amount given output amount
        pass

    def get_apy(self, pool_state: Dict) -> Decimal:
        # Implement APY calculation logic
        pass

    def get_tvl(
        self, 
        pool_state: Dict,
        fixed_parameters: Dict,
        pool_tokens: Dict[str, Token]
    ) -> int:
        tvl = 0

        for address, token in pool_tokens.items():
            token_balance_key = address.lower() + '_balance'
            tvl_token = int(pool_state[token_balance_key])
            tvl_token *= int(token.reference_price)
            tvl_token //= 10 ** token.decimals
            tvl += tvl_token
        
        return tvl