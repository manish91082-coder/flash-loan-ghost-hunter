from eth_account.messages import encode_typed_data
from web3 import Web3

class ExecutionIntentBuilder:
    def __init__(self, private_key, verifying_contract, chain_id):
        self.w3 = Web3()
        self.account = self.w3.eth.account.from_key(private_key)
        self.verifying_contract = verifying_contract
        self.chain_id = chain_id
        
    def build_typed_data(self, intent_dict):
        """
        Builds the EIP-712 typed data payload matching the Solidity struct.
        """
        return {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "ExecutionIntent": [
                    {"name": "executionId", "type": "bytes32"},
                    {"name": "providerType", "type": "uint8"},
                    {"name": "providerAddress", "type": "address"},
                    {"name": "tokenBorrow", "type": "address"},
                    {"name": "amountBorrow", "type": "uint256"},
                    {"name": "swap1Type", "type": "uint8"},
                    {"name": "routerA", "type": "address"},
                    {"name": "pathA", "type": "bytes"},
                    {"name": "minAmountOut1", "type": "uint256"},
                    {"name": "swap2Type", "type": "uint8"},
                    {"name": "routerB", "type": "address"},
                    {"name": "pathB", "type": "bytes"},
                    {"name": "minAmountOutFinal", "type": "uint256"},
                    {"name": "minimumOnChainSurplus", "type": "uint256"},
                    {"name": "maximumGasLimit", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"}
                ]
            },
            "primaryType": "ExecutionIntent",
            "domain": {
                "name": "PhantomX Executor",
                "version": "1",
                "chainId": self.chain_id,
                "verifyingContract": self.verifying_contract
            },
            "message": intent_dict
        }
        
    def sign_intent(self, intent_dict):
        typed_data = self.build_typed_data(intent_dict)
        signed_message = self.account.sign_typed_data(full_message=typed_data)
        
        # Keep it as a dict but append the signature
        result = dict(intent_dict)
        result['signature'] = signed_message.signature
        return result
        
    def build_calldata(self, intent_dict):
        """
        Builds the actual ABI-encoded calldata for the executeOpportunity function.
        Used for exact gas estimation and eth_call simulation.
        """
        # Exact Canonical ABI for executeOpportunity
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

        signed = self.sign_intent(intent_dict)
        
        contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.verifying_contract), 
            abi=EXECUTOR_ABI
        )

        intent_tuple = (
            signed["executionId"],
            signed["providerType"],
            self.w3.to_checksum_address(signed["providerAddress"]),
            self.w3.to_checksum_address(signed["tokenBorrow"]),
            signed["amountBorrow"],
            signed["swap1Type"],
            self.w3.to_checksum_address(signed["routerA"]),
            signed["pathA"],
            signed["minAmountOut1"],
            signed["swap2Type"],
            self.w3.to_checksum_address(signed["routerB"]),
            signed["pathB"],
            signed["minAmountOutFinal"],
            signed["minimumOnChainSurplus"],
            signed["maximumGasLimit"],
            signed["deadline"],
            signed["signature"]
        )

        encoded_args = contract.encodeABI(fn_name="executeOpportunity", args=[intent_tuple])
        return bytes.fromhex(encoded_args[2:])

class PathEncoder:
    @staticmethod
    def build_v2_path(tokens):
        from eth_abi import encode
        return encode(['address[]'], [list(tokens)])

    @staticmethod
    def build_v3_path_single(token_in, fee, token_out):
        return Web3.to_bytes(hexstr=token_in) + int(fee).to_bytes(3, 'big') + Web3.to_bytes(hexstr=token_out)

    @staticmethod
    def build_v3_path_triangular(token_a, fee1, token_b, fee2, token_c, fee3, token_end):
        return (
            Web3.to_bytes(hexstr=token_a) + 
            int(fee1).to_bytes(3, 'big') + 
            Web3.to_bytes(hexstr=token_b) + 
            int(fee2).to_bytes(3, 'big') + 
            Web3.to_bytes(hexstr=token_c) +
            int(fee3).to_bytes(3, 'big') + 
            Web3.to_bytes(hexstr=token_end)
        )

    @staticmethod
    def build_yield_path(protocol, action, token):
        # Placeholder for yield farming stake/unstake calldata packing
        # format: action_id (1 byte) + token_address (20 bytes) + protocol_id (1 byte)
        action_id = 1 if action == "stake" else 0
        protocol_id = 1 # e.g. 1 for Aave, 2 for Compound
        return int(action_id).to_bytes(1, 'big') + Web3.to_bytes(hexstr=token) + int(protocol_id).to_bytes(1, 'big')

    @staticmethod
    def build_statistical_path(token_a, token_b):
        # Mean reversion placeholder packing
        return Web3.to_bytes(hexstr=token_a) + Web3.to_bytes(hexstr=token_b)

    @staticmethod
    def build_bridge_path(chain_a, chain_b, token):
        # Cross-chain bridge calldata packing
        return int(chain_a).to_bytes(32, 'big') + int(chain_b).to_bytes(32, 'big') + Web3.to_bytes(hexstr=token)

    @staticmethod
    def build_mev_path(target_tx_hash, token):
        # Sandwich MEV payload (target tx hash + token)
        return Web3.to_bytes(hexstr=target_tx_hash) + Web3.to_bytes(hexstr=token)
