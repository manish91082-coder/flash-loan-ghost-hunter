import fs from 'node:fs/promises';
import { keccak256 } from 'ethers';

const EXECUTOR = '0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286';
const DEPLOYER = '0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e';
const DEPLOY_TX = '0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a';
const RPCS = [
  'https://polygon.drpc.org',
  'https://tenderly.rpc.polygon.community/',
  'https://polygon.publicnode.com',
  'https://polygon-public.nodies.app/',
  'https://1rpc.io/matic',
  'https://polygon.api.onfinality.io/public',
  'https://polygon-mainnet.gateway.tatum.io/',
  'https://rpc-mainnet.matic.quiknode.pro',
];

async function rpc(url, method, params) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  const started = performance.now();
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
    return { result: body.result, latency_ms: performance.now() - started };
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
  const compiledHash = keccak256('0x' + compiled).toLowerCase();

  const attempts = [];
  for (const url of RPCS) {
    try {
      const chain = await rpc(url, 'eth_chainId', []);
      required(Number.parseInt(chain.result, 16) === 137, `WRONG_CHAIN_${chain.result}`);
      const block = await rpc(url, 'eth_blockNumber', []);
      const code = await rpc(url, 'eth_getCode', [EXECUTOR, 'latest']);
      const ownerRaw = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x8da5cb5b' }, 'latest']);
      const domain = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x3644e515' }, 'latest']);
      const pausedRaw = await rpc(url, 'eth_call', [{ to: EXECUTOR, data: '0x5c975abb' }, 'latest']);
      const tx = await rpc(url, 'eth_getTransactionByHash', [DEPLOY_TX]);
      const receipt = await rpc(url, 'eth_getTransactionReceipt', [DEPLOY_TX]);
      required(tx.result && receipt.result, 'DEPLOYMENT_RECORD_NOT_FOUND');
      const deployBlock = receipt.result.blockNumber;
      required(deployBlock, 'DEPLOYMENT_BLOCK_MISSING');
      const creationCode = await rpc(url, 'eth_getCode', [EXECUTOR, deployBlock]);
      const owner = '0x' + ownerRaw.result.slice(-40);
      attempts.push({
        rpc: url,
        status: 'SUCCESS',
        latency_ms_total: Number((chain.latency_ms + block.latency_ms + code.latency_ms + ownerRaw.latency_ms + domain.latency_ms + pausedRaw.latency_ms + tx.latency_ms + receipt.latency_ms + creationCode.latency_ms).toFixed(3)),
        checks: {
          chain_id: Number.parseInt(chain.result, 16),
          latest_block: Number.parseInt(block.result, 16),
          executor: EXECUTOR,
          deployed_runtime_bytes: (code.result.length - 2) / 2,
          deployed_runtime_hash: keccak256(code.result),
          compiled_runtime_bytes: compiled.length / 2,
          compiled_runtime_hash: compiledHash,
          runtime_hash_match: keccak256(code.result).toLowerCase() === compiledHash,
          owner,
          domain_separator: domain.result,
          paused: pausedRaw.result.toLowerCase() === '0x' + '0'.repeat(63) + '1',
          deployment: {
            tx: DEPLOY_TX,
            from: tx.result.from,
            to: tx.result.to,
            status: receipt.result.status,
            contract_address: receipt.result.contractAddress,
            block: Number.parseInt(deployBlock, 16),
            runtime_hash_at_creation: keccak256(creationCode.result),
            runtime_match_at_creation: keccak256(creationCode.result).toLowerCase() === keccak256(code.result).toLowerCase(),
          },
        },
      });
    } catch (error) {
      attempts.push({ rpc: url, status: 'FAILED', error: String(error) });
    }
  }

  const successes = attempts.filter((x) => x.status === 'SUCCESS');
  const evidence = {
    status: successes.length >= 2 ? 'PROBED' : 'BLOCKED',
    timestamp_utc: new Date().toISOString(),
    executor: EXECUTOR,
    deployer: DEPLOYER,
    deployment_tx: DEPLOY_TX,
    required_rpc_consensus: 2,
    attempts,
    broadcasts: 0,
  };

  if (successes.length >= 2) {
    successes.sort((a, b) => a.latency_ms_total - b.latency_ms_total);
    const primary = successes[0].checks;
    const peer = successes[1].checks;
    required(primary.chain_id === 137 && peer.chain_id === 137, 'CHAIN_ID_MISMATCH');
    required(primary.deployed_runtime_hash.toLowerCase() === peer.deployed_runtime_hash.toLowerCase(), 'RPC_RUNTIME_HASH_DIVERGENCE');
    required(primary.compiled_runtime_hash === peer.compiled_runtime_hash, 'COMPILED_HASH_DIVERGENCE');
    required(primary.owner.toLowerCase() === peer.owner.toLowerCase(), 'RPC_OWNER_DIVERGENCE');
    required(primary.domain_separator.toLowerCase() === peer.domain_separator.toLowerCase(), 'RPC_DOMAIN_DIVERGENCE');
    required(primary.deployment.contract_address.toLowerCase() === EXECUTOR.toLowerCase(), 'CREATED_CONTRACT_MISMATCH');
    required(primary.deployment.from.toLowerCase() === DEPLOYER.toLowerCase(), 'DEPLOYER_MISMATCH');
    required(primary.deployment.status === '0x1', 'DEPLOYMENT_RECEIPT_FAILED');
    required(primary.owner.toLowerCase() === DEPLOYER.toLowerCase(), 'OWNER_MISMATCH');
    required(primary.compiled_runtime_hash === primary.deployed_runtime_hash.toLowerCase(), 'RUNTIME_HASH_MISMATCH');
    required(primary.domain_separator.startsWith('0x') && primary.domain_separator.length === 66, 'DOMAIN_SEPARATOR_INVALID');
    required(primary.deployed_runtime_bytes > 0, 'NO_DEPLOYED_RUNTIME');
    evidence.selected = primary;
    evidence.peer = peer;
  }

  await fs.mkdir('evidence', { recursive: true });
  await fs.writeFile('evidence/p0a-runtime-identity.json', JSON.stringify(evidence, null, 2) + '\n');
  console.log(JSON.stringify(evidence, null, 2));

  required(successes.length >= 2, 'INSUFFICIENT_RPC_CONSENSUS');
  console.log('P0-A executor runtime identity: PASS');
  console.log('No transaction was signed or broadcast.');
}

await main();
