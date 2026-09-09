import pytest
import os
import solcx
from web3 import Web3
from eth_account import Account
import time
import sys

# Ensure execution is in path to import intent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from execution.intent import ExecutionIntentBuilder

@pytest.fixture(scope="module")
def w3():
    # Connect to the local Anvil instance running on port 8545
    return Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

@pytest.fixture(scope="module")
def owner(w3):
    return w3.eth.accounts[0]

@pytest.fixture(scope="module")
def attacker(w3):
    return w3.eth.accounts[1]
    
@pytest.fixture(scope="module")
def owner_key():
    # Anvil's first deterministic account private key
    return "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

@pytest.fixture(scope="module")
def attacker_key():
    # Anvil's second deterministic account private key
    return "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

@pytest.fixture(scope="module")
def executor_contract(w3, owner_key, owner):
    solcx.install_solc('0.8.19')
    with open('contracts/PhantomX_Production_Executor.sol', 'r') as f:
        source = f.read()
    
    compiled = solcx.compile_source(
        source, 
        output_values=['abi', 'bin'], 
        solc_version='0.8.19',
        optimize=True,
        optimize_runs=200,
        via_ir=True
    )
    contract_interface = compiled['<stdin>:PhantomX_Production_Executor']
    
    Executor = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    
    # Deploy contract using Anvil's unlocked account 0
    tx_hash = Executor.constructor().transact({'from': owner})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface['abi']
    )
    return contract, owner

@pytest.fixture(scope="module")
def base_intent_dict(w3):
    return {
        'executionId': os.urandom(32),
        'providerType': 0, # AAVE
        'providerAddress': w3.to_checksum_address("0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"),
        'tokenBorrow': w3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
        'amountBorrow': 1000 * 10**6,
        'swap1Type': 1, # V3
        'routerA': w3.to_checksum_address("0x2626664c2603336E57B271c5C0b26F421741e481"),
        'pathA': b'\x00' * 43, # stub for test
        'minAmountOut1': 0, # calculated slippage
        'swap2Type': 0, # V2
        'routerB': w3.to_checksum_address("0x8cFE327CEc66d1C090Dd72bd0FF11d690C33a2Eb"),
        'pathB': b'\x00' * 43, # stub for test
        'minAmountOutFinal': 1000 * 10**6,
        'minimumOnChainSurplus': 1 * 10**6,
        'maximumGasLimit': 3000000,
        'deadline': int(time.time()) + 1000
    }

def to_tuple(signed_dict):
    return (
        signed_dict['executionId'],
        signed_dict['providerType'],
        signed_dict['providerAddress'],
        signed_dict['tokenBorrow'],
        signed_dict['amountBorrow'],
        signed_dict['swap1Type'],
        signed_dict['routerA'],
        signed_dict['pathA'],
        signed_dict['minAmountOut1'],
        signed_dict['swap2Type'],
        signed_dict['routerB'],
        signed_dict['pathB'],
        signed_dict['minAmountOutFinal'],
        signed_dict['minimumOnChainSurplus'],
        signed_dict['maximumGasLimit'],
        signed_dict['deadline'],
        signed_dict['signature']
    )

def test_unauthorized_callback_rejected(w3, attacker, executor_contract):
    contract, owner_account = executor_contract
    
    with pytest.raises(Exception) as e:
        contract.functions.executeOperation(
            w3.to_checksum_address("0x0000000000000000000000000000000000000001"),
            100,
            10,
            contract.address,
            b""
        ).transact({'from': attacker})
        
    assert "Untrusted callback" in str(e.value) or "revert" in str(e.value).lower()

def test_valid_signature_mutated_data_rejected(w3, attacker, executor_contract, owner_key, base_intent_dict):
    contract, owner_account = executor_contract
    chain_id = w3.eth.chain_id
    
    # 1. Sign original intent properly
    builder = ExecutionIntentBuilder(owner_key, contract.address, chain_id)
    signed_intent = builder.sign_intent(base_intent_dict)
    
    # 2. Attacker mutates the amount to borrow, trying to reuse signature
    signed_intent['amountBorrow'] = 5000000 * 10**6
    payload = to_tuple(signed_intent)
    
    with pytest.raises(Exception) as e:
        contract.functions.executeOpportunity(payload).transact({'from': attacker})
        
    assert "Invalid Intent Signature" in str(e.value) or "revert" in str(e.value).lower()

def test_wrong_signer_rejected(w3, attacker, attacker_key, executor_contract, base_intent_dict):
    contract, owner_account = executor_contract
    chain_id = w3.eth.chain_id
    
    # Attacker signs with their own key
    builder = ExecutionIntentBuilder(attacker_key, contract.address, chain_id)
    signed_intent = builder.sign_intent(base_intent_dict)
    payload = to_tuple(signed_intent)
    
    with pytest.raises(Exception) as e:
        contract.functions.executeOpportunity(payload).transact({'from': attacker})
        
    assert "Invalid Intent Signature" in str(e.value) or "revert" in str(e.value).lower()

def test_cross_domain_replay_rejected(w3, attacker, owner_key, executor_contract, base_intent_dict):
    contract, owner_account = executor_contract
    chain_id = w3.eth.chain_id
    
    # Sign intent but with wrong chain ID (cross-chain replay)
    builder = ExecutionIntentBuilder(owner_key, contract.address, chain_id + 1)
    signed_intent = builder.sign_intent(base_intent_dict)
    payload = to_tuple(signed_intent)
    
    with pytest.raises(Exception) as e:
        contract.functions.executeOpportunity(payload).transact({'from': attacker})
        
    assert "Invalid Intent Signature" in str(e.value) or "revert" in str(e.value).lower()

def test_expired_intent_rejected(w3, attacker, owner_key, executor_contract, base_intent_dict):
    contract, owner_account = executor_contract
    chain_id = w3.eth.chain_id
    
    expired_dict = dict(base_intent_dict)
    expired_dict['deadline'] = int(time.time()) - 1000 # Past deadline
    
    builder = ExecutionIntentBuilder(owner_key, contract.address, chain_id)
    signed_intent = builder.sign_intent(expired_dict)
    payload = to_tuple(signed_intent)
    
    with pytest.raises(Exception) as e:
        contract.functions.executeOpportunity(payload).transact({'from': attacker})
        
    assert "Expired" in str(e.value) or "revert" in str(e.value).lower()

def test_zero_address_ownership_transfer_rejected(w3, executor_contract, owner):
    contract, owner_account = executor_contract
    
    with pytest.raises(Exception) as e:
        contract.functions.transferOwnership(
            w3.to_checksum_address("0x0000000000000000000000000000000000000000")
        ).transact({'from': owner})
        
    assert "Zero address" in str(e.value) or "revert" in str(e.value).lower()
