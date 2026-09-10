import fs from 'node:fs/promises';
import { keccak256 } from 'ethers';

const EXECUTOR = '0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286';
const DEPLOYER = '0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e';
const DEPLOY_TX = '0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a';
const RPCS = [
  'https://polygon-bor.publicnode.com',
  'https://polygon-rpc.com',
  'https://rpc-mainnet.maticvigil.com',
  'https://1rpc.io/matic',
];

async function rpc(url, method, params) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`HTTP_${response.status}`);
    const body = await response.json();
    if (body.error) throw new Error(JSON.stringify(body.error));
    return body.result;
  } finally {
    clearTimeout(timer);
  }
}

function required(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const source = await fs.readFile('contracts/PhantomX_Production_Executor.sol', 'utf8');
  const compiler = (await import('solc')).default;
  const input = {
    language: 'Solidity',
    sources: { 'contracts/PhantomX_Production_Executor.sol': { content: source } },
    settings: {
      optimizer: { enabled: true, runs: 200 },
      viaIR: true,
      outputSelection: { '*': { '*': ['evm.deployedBytecode.object'] } },
    },
  };
  const output = JSON.parse(compiler.compile(JSON.stringify(input)));
  const errors = (output.errors ?? []).filter((e) => e.severity === 'error');
  required(errors.length === 0, `SOLC_ERRORS:\n${errors.map((e) => e.formattedMessage).join('\n')}`);
  const compiled = output.contracts['contracts/PhantomX_Production_Executor.sol'].PhantomX_Production_Executor.evm.deployedBytecode.object;
  required(typeof compiled === 'string' && compiled.length > 0, 'EMPTY_COMPILED_RUNTIME');

  const attempts = [];
  let selected = null;
  for (const url of RPCS) {
    try {
      const chainId = Number.parseInt(await rpc(url, 'eth_chainId', []), 16);
      required(chainId === 137, `WRONG_CHAIN_${chainId}`);
      const latestBlockHex = await rpc(url, 'eth_blockNumber', []);
      const code = await rpc(url, 'eth_getCode', [EXECUTOR, 'latest']);
      const ownerRaw = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x8da5cb5b' }, 'latest']);
      const domain = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x3644e515' }, 'latest']);
      const pausedRaw = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x5c975abb' }, 'latest']);
      const tx = await rpc(url, 'eth_getTransactionByHash', [DEPLOY_TX]);
      const receipt = await rpc(url, 'eth_getTransactionReceipt', [DEPLOY_TX]);
      required(typeof tx === 'object' && tx !== null, 'DEPLOY_TX_NOT_FOUND');
      required(typeof receipt === 'object' && receipt !== null, 'DEPLOY_RECEIPT_NOT_FOUND');
      const deployBlock = receipt.blockNumber;
      const creationCode = deployBlock ? await rpc(url, 'eth_getCode', [EXECUTOR, deployBlock]) : null;
      const owner = '0x' + ownerRaw.slice(-40);
      const record = {
        rpc: url,
        chain_id: chainId,
        latest_block: Number.parseInt(latestBlockHex, 16),
        executor: EXECUTOR,
        deployed_runtime_bytes: (code.length - 2) / 2,
        deployed_runtime_hash: keccak256(code),
        compiled_runtime_bytes: compiled.length / 2,
        compiled_runtime_hash: keccak256('0x' + compiled),
        runtime_hash_match: keccak256(code).toLowerCase() === keccak256('0x' + compiled).toLowerCase(),
        owner,
        domain_separator: domain,
        paused: pausedRaw.toLowerCase() === '0x' + '0'.repeat(63) + '1',
        deployment: {
          tx: DEPLOY_TX,
          from: tx.from,
          to: tx.to,
          status: receipt.status,
          contract_address: receipt.contractAddress,
          block: deployBlock ? Number.parseInt(deployBlock, 16) : null,
          runtime_hash_at_creation: creationCode ? keccak256(creationCode) : null,
          runtime_match_at_creation: creationCode ? keccak256(creationCode).toLowerCase() === keccak256(code).toLowerCase() : null,
        },
      };
      attempts.push({ rpc: url, status: 'SUCCESS', checks: record });
      selected = record;
      break;
    } catch (error) {
      attempts.push({ rpc: url, status: 'FAILED', error: String(error) });
    }
  }

  const evidence = {
    status: selected ? 'PROBED' : 'BLOCKED',
    timestamp_utc: new Date().toISOString(),
    executor: EXECUTOR,
    deployer: DEPLOYER,
    deployment_tx: DEPLOY_TX,
    attempts,
    selected,
    broadcasts: 0,
  };
  await fs.mkdir('evidence', { recursive: true });
  await fs.writeFile('evidence/p0a-runtime-identity.json', JSON.stringify(evidence, null, 2) + '\n');
  console.log(JSON.stringify(evidence, null, 2));

  required(selected !== null, 'NO_VALID_RPC');
  required(selected.chain_id === 137, 'CHAIN_ID_MISMATCH');
  required(selected.deployed_runtime_bytes > 0, 'NO_DEPLOYED_RUNTIME');
  required(selected.owner.toLowerCase() === DEPLOYER.toLowerCase(), 'OWNER_MISMATCH');
  required(selected.deployment.from.toLowerCase() === DEPLOYER.toLowerCase(), 'DEPLOYER_MISMATCH');
  required(selected.deployment.contract_address.toLowerCase() === EXECUTOR.toLowerCase(), 'CREATED_CONTRACT_MISMATCH');
  required(selected.deployment.status === '0x1', 'DEPLOYMENT_RECEIPT_FAILED');
  required(selected.domain_separator.startsWith('0x') && selected.domain_separator.length === 66, 'DOMAIN_SEPARATOR_INVALID');
  required(selected.runtime_hash_match === true, 'RUNTIME_HASH_MISMATCH');
  console.log('P0-A executor runtime identity: PASS');
  console.log('No transaction was signed or broadcast.');
}

await main();
