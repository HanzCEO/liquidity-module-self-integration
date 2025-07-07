import web3
import sys

rpc = sys.argv[2] if len(sys.argv) > 2 else "https://eth.llamarpc.com"
w3 = web3.Web3(web3.Web3.HTTPProvider(rpc))

poolAddr = sys.argv[1] if len(sys.argv) > 1 else None
if not poolAddr:
	print("Usage: python fetch_all.py <pool_address> [RPC_URL]")
	sys.exit(1)

generalAbi = [
	{
		"inputs": [],
		"name": "ONE",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "asset",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAssetBreakdown",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "totalIdle",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "totalDebt",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "totalDebtMin",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "totalDebtMax",
						"type": "uint256"
					}
				],
				"internalType": "struct IAutopool.AssetBreakdown",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getDebtReportingQueue",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "destVault",
				"type": "address"
			}
		],
		"name": "getDestinationInfo",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "cachedDebtValue",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "cachedMinDebtValue",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "cachedMaxDebtValue",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "lastReport",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "ownedShares",
						"type": "uint256"
					}
				],
				"internalType": "struct AutopoolDebt.DestinationInfo",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getDestinations",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getProfitUnlockSettings",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint48",
						"name": "unlockPeriodInSeconds",
						"type": "uint48"
					},
					{
						"internalType": "uint48",
						"name": "fullProfitUnlockTime",
						"type": "uint48"
					},
					{
						"internalType": "uint48",
						"name": "lastProfitUnlockTime",
						"type": "uint48"
					},
					{
						"internalType": "uint256",
						"name": "profitUnlockRate",
						"type": "uint256"
					}
				],
				"internalType": "struct IAutopool.ProfitUnlockSettings",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "isShutdown",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "oldestDebtReporting",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "paused",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalSupply",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "shares",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	
	{
		"inputs": [],
		"name": "getUnderlyerCeilingPrice",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getUnderlyerFloorPrice",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

pool = w3.eth.contract(address=poolAddr, abi=generalAbi)


oldest_debt_reporting = pool.functions.oldestDebtReporting().call()

total_supply = pool.functions.totalSupply().call()
asset_breakdown = pool.functions.getAssetBreakdown().call()
previous_asset_breakdown = { # just simulated
	"totalIdle": asset_breakdown[0] * 0.8,
	"totalDebt": asset_breakdown[1] * 0.8,
	"totalDebtMin": asset_breakdown[2] * 0.8,
	"totalDebtMax": asset_breakdown[3] * 0.8
}
previous_total_supply = total_supply * 0.8
days = 5

paused = pool.functions.paused().call()
shutdown = pool.functions.isShutdown().call()
pus = pool.functions.getProfitUnlockSettings().call()
profit_unlock_settings = {
	"unlockPeriodInSeconds": pus[0],
	"fullProfitUnlockTime": pus[1],
	"lastProfitUnlockTime": pus[2],
	"profitUnlockRate": pus[3]
}
debt_report_queue = pool.functions.getDebtReportingQueue().call()

destination_info = {}
destinations = pool.functions.getDestinations().call()
for dest in destinations:
	destContract = w3.eth.contract(address=dest, abi=generalAbi)
	
	with w3.batch_requests() as batch:
		batch.add(pool.functions.getDestinationInfo(dest))
		batch.add(destContract.functions.balanceOf(poolAddr))
		batch.add(destContract.functions.getUnderlyerCeilingPrice())
		batch.add(destContract.functions.getUnderlyerFloorPrice())
		batch.add(destContract.functions.ONE())

		res1, currentShares, underlyerCeilingPrice, underlyerFloorPrice, ONE = batch.execute()
		destl = dest.lower()
		destination_info[destl] = {}
		(_, min_, max_, last, owned) = res1
		destination_info[destl]["lastReport"] = last
		destination_info[destl]["ownedShares"] = owned
		destination_info[destl]["cachedMaxDebtValue"] = max_
		destination_info[destl]["cachedMinDebtValue"] = min_

		destination_info[destl]["currentShares"] = currentShares
		destination_info[destl]["underlyerCeilingPrice"] = underlyerCeilingPrice
		destination_info[destl]["underlyerFloorPrice"] = underlyerFloorPrice
		destination_info[destl]["ONE"] = ONE

pool_state = {
	"oldestDebtReporting": oldest_debt_reporting,
	"totalSupply": total_supply,
	"assetBreakdown": {
		"totalIdle": asset_breakdown[0],
		"totalDebt": asset_breakdown[1],
		"totalDebtMin": asset_breakdown[2],
		"totalDebtMax": asset_breakdown[3]
	},
	"previousAssetBreakdown": previous_asset_breakdown,
	"previousTotalSupply": previous_total_supply,
	"days": 30, # simulation
	"paused": paused,
	"shutdown": shutdown,
	"profitUnlockSettings": profit_unlock_settings,
	"debtReportQueue": [debt_report_queue[i].lower() for i in range(len(debt_report_queue))],
	"destinationInfo": destination_info,
}

fixed_parameters = {
	"vaultTokenAddress": poolAddr,
	"asset": pool.functions.asset().call(),
}

print(f"""
{pool_state = }

{fixed_parameters = }
""")