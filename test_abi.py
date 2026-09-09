from web3 import Web3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from execution.intent import ExecutionIntentBuilder, PathEncoder

w3 = Web3()
builder = ExecutionIntentBuilder("0x" + "1" * 64, "0x9c48858d4DF2A57ebB1400A9F9e1fdb702e8B9A0", 8453)

EXECUTOR_ABI = [{
    "inputs": [
      {
        "components": [
          {"internalType": "bytes32", "name": "executionId", "type": "bytes32"},
          {"internalType": "uint8", "name": "providerType", "type": "uint8"},
          {"internalType": "address", "name": "providerAddress", "type": "address"},
          {"internalType": "address", "name": "tokenBorrow", "type": "address"},
          {"internalType": "uint256", "name": "amountBorrow", "type": "uint256"},
          {"internalType": "uint8", "name": "swap1Type", "type": "uint8"},
          {"internalType": "address", "name": "routerA", "type": "address"},
          {"internalType": "bytes", "name": "pathA", "type": "bytes"},
          {"internalType": "uint256", "name": "minAmountOut1", "type": "uint256"},
          {"internalType": "uint8", "name": "swap2Type", "type": "uint8"},
          {"internalType": "address", "name": "routerB", "type": "address"},
          {"internalType": "bytes", "name": "pathB", "type": "bytes"},
          {"internalType": "uint256", "name": "minAmountOutFinal", "type": "uint256"},
          {"internalType": "uint256", "name": "minimumOnChainSurplus", "type": "uint256"},
          {"internalType": "uint256", "name": "maximumGasLimit", "type": "uint256"},
          {"internalType": "uint256", "name": "deadline", "type": "uint256"},
          {"internalType": "bytes", "name": "signature", "type": "bytes"}
        ],
        "internalType": "struct PhantomX_Production_Executor.ExecutionIntent",
        "name": "intent",
        "type": "tuple"
      }
    ],
    "name": "executeOpportunity",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}]

intent_data = {
    "executionId": b'\x01' * 32,
    "providerType": 1,
    "providerAddress": "0x1111111111111111111111111111111111111111",
    "tokenBorrow": "0x2222222222222222222222222222222222222222",
    "amountBorrow": 1000,
    "swap1Type": 1,
    "routerA": "0x3333333333333333333333333333333333333333",
    "pathA": b'\x02' * 64,
    "minAmountOut1": 900,
    "swap2Type": 2,
    "routerB": "0x4444444444444444444444444444444444444444",
    "pathB": b'\x03' * 64,
    "minAmountOutFinal": 1100,
    "minimumOnChainSurplus": 0,
    "maximumGasLimit": 1000000,
    "deadline": 9999999999
}

signed = builder.sign_intent(intent_data)

contract = w3.eth.contract(address="0x9c48858d4DF2A57ebB1400A9F9e1fdb702e8B9A0", abi=EXECUTOR_ABI)

intent_tuple = (
    signed["executionId"],
    signed["providerType"],
    signed["providerAddress"],
    signed["tokenBorrow"],
    signed["amountBorrow"],
    signed["swap1Type"],
    signed["routerA"],
    signed["pathA"],
    signed["minAmountOut1"],
    signed["swap2Type"],
    signed["routerB"],
    signed["pathB"],
    signed["minAmountOutFinal"],
    signed["minimumOnChainSurplus"],
    signed["maximumGasLimit"],
    signed["deadline"],
    signed["signature"]
)

encoded = contract.encodeABI(fn_name="executeOpportunity", args=[intent_tuple])
print("ENCODED:", encoded)
