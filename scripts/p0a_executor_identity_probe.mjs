import fs from 'node:fs/promises';
import { keccak256 } from 'ethers';

const EXECUTOR = '0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286';
const DEPLOYER = '0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e';
const DEPLOY_TX = '0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a';
const RPCS = [
  'https://rpc-mainnet.matic.quiknode.pro',
  'https://polygon.drpc.org',
  'https://polygon.publicnode.com',
  'https://1rpc.io/matic',
  'https://polygon.api.onfinality.io/public',
  'https://polygon-mainnet.gateway.tatum.io/',
  'https://polygon-rpc.com',
  'https://polygon.blockpi.network/v1/rpc/public',
];

function required(condition, message) { if (!condition) throw new Error(message); }

async function rpc(url, method, params) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  const started = performance.now();
  try {
    const response = await fetch(url, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), signal: controller.signal,
    });
    if (!response.ok) throw new Error(`HTTP_${response.status}`);
    const body = await response.json();
    if (body.error) throw new Error(JSON.stringify(body.error));
    return { result: body.result, latency_ms: performance.now() - started };
  } finally { clearTimeout(timer); }
}

async function safeCall(url, method, params) {
  try { const r = await rpc(url, method, params); return { ok:true, result:r.result, latency_ms:r.latency_ms }; }
  catch (error) { return { ok:false, error:String(error) }; }
}

async function compileRuntime(path, contractName, compiler, settings, sourceKey=path) {
  const source = await fs.readFile(path, 'utf8');
  const input = {
    language: 'Solidity',
    sources: { [sourceKey]: { content: source } },
    settings: { ...settings, outputSelection: { '*': { '*': ['evm.deployedBytecode.object'] } } },
  };
  const output = JSON.parse(compiler.compile(JSON.stringify(input)));
  const errors = (output.errors ?? []).filter((e) => e.severity === 'error');
  required(errors.length === 0, `SOLC_ERRORS_${path}_${sourceKey}:\n${errors.map(e=>e.formattedMessage).join('\n')}`);
  const artifact = output.contracts[sourceKey]?.[contractName];
  required(artifact, `NO_CONTRACT_${contractName}_${sourceKey}`);
  const runtime = artifact.evm?.deployedBytecode?.object;
  required(typeof runtime === 'string' && runtime.length > 0, `EMPTY_RUNTIME_${contractName}_${sourceKey}`);
  return { contract:contractName, source_key:sourceKey, compiler_version:compiler.version(), optimizer:settings.optimizer ?? {enabled:false}, viaIR:settings.viaIR ?? false, bytes:runtime.length/2, hash:keccak256('0x'+runtime) };
}

async function main() {
  const compiler119=(await import('solc')).default;
  const compiler120=(await import('solc0820')).default;
  const hardened=await compileRuntime('contracts/PhantomX_Production_Executor.sol','PhantomX_Production_Executor',compiler119,{optimizer:{enabled:true,runs:200},viaIR:true},'contracts/PhantomX_Production_Executor.sol');
  const historicalVariants=[];
  const historicalSettings={optimizer:{enabled:false,runs:200},viaIR:false};
  for (const key of ['<stdin>','PhantomXMVP.sol','contracts/src/PhantomXMVP.sol','flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol']) {
    historicalVariants.push(await compileRuntime('flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol','PhantomXMVP',compiler120,historicalSettings,key));
  }

  const attempts=[];
  for (const url of RPCS) {
    const a={rpc:url};
    const chain=await safeCall(url,'eth_chainId',[]);
    a.chain_id=chain.ok?Number.parseInt(chain.result,16):null;
    if (!chain.ok || a.chain_id!==137) { a.status='FAILED_CHAIN'; a.error=chain.ok?`WRONG_CHAIN_${a.chain_id}`:chain.error; attempts.push(a); continue; }
    const block=await safeCall(url,'eth_blockNumber',[]);
    const code=await safeCall(url,'eth_getCode',[EXECUTOR,'latest']);
    const owner=await safeCall(url,'eth_call',[{to:EXECUTOR,data:'0x8da5cb5b'},'latest']);
    const domain=await safeCall(url,'eth_call',[{to:EXECUTOR,data:'0x3644e515'},'latest']);
    const paused=await safeCall(url,'eth_call',[{to:EXECUTOR,data:'0x5c975abb'},'latest']);
    const tx=await safeCall(url,'eth_getTransactionByHash',[DEPLOY_TX]);
    const receipt=await safeCall(url,'eth_getTransactionReceipt',[DEPLOY_TX]);
    a.status='PARTIAL';
    a.latest_block=block.ok?Number.parseInt(block.result,16):null;
    a.executor_code_bytes=code.ok?Math.max(0,(code.result.length-2)/2):null;
    a.executor_code_hash=code.ok?keccak256(code.result):null;
    a.owner=owner.ok&&owner.result.length===66?'0x'+owner.result.slice(-40):null;
    a.domain_separator=domain.ok?domain.result:null;
    a.paused=paused.ok?paused.result:null;
    a.deployment={from:tx.ok&&tx.result?tx.result.from:null,to:tx.ok&&tx.result?tx.result.to:null,status:receipt.ok&&receipt.result?receipt.result.status:null,contract_address:receipt.ok&&receipt.result?receipt.result.contractAddress:null,block:receipt.ok&&receipt.result?.blockNumber?Number.parseInt(receipt.result.blockNumber,16):null};
    a.stage_errors={block:block.ok?null:block.error,code:code.ok?null:code.error,owner:owner.ok?null:owner.error,domain:domain.ok?null:domain.error,paused:paused.ok?null:paused.error,tx:tx.ok?null:tx.error,receipt:receipt.ok?null:receipt.error};
    a.core_ready=Boolean(code.ok&&code.result!=='0x'&&owner.ok&&tx.ok&&receipt.ok);
    a.owner_match=a.owner?a.owner.toLowerCase()===DEPLOYER.toLowerCase():false;
    a.deployment_sender_match=a.deployment.from?a.deployment.from.toLowerCase()===DEPLOYER.toLowerCase():false;
    a.deployment_contract_match=a.deployment.contract_address?a.deployment.contract_address.toLowerCase()===EXECUTOR.toLowerCase():false;
    a.deployment_receipt_success=a.deployment.status==='0x1';
    a.domain_valid=typeof a.domain_separator==='string' && /^0x[0-9a-fA-F]{64}$/.test(a.domain_separator);
    a.hardened_source_hash_match=a.executor_code_hash?a.executor_code_hash.toLowerCase()===hardened.hash.toLowerCase():false;
    a.historical_variant_matches=historicalVariants.filter(v=>a.executor_code_hash&&a.executor_code_hash.toLowerCase()===v.hash.toLowerCase()).map(v=>v.source_key);
    attempts.push(a);
  }

  const core=attempts.filter(a=>a.core_ready);
  const evidence={status:'BLOCKED',timestamp_utc:new Date().toISOString(),executor:EXECUTOR,deployer:DEPLOYER,deployment_tx:DEPLOY_TX,required_rpc_consensus:2,artifact_candidates:{current_hardened:hardened,historical_phantomxmvp_variants:historicalVariants},attempts,broadcasts:0};
  if (core.length>=2) {
    core.sort((x,y)=>(x.latest_block??0)-(y.latest_block??0));
    const primary=core[core.length-1]; const peer=core[core.length-2];
    required(primary.executor_code_hash.toLowerCase()===peer.executor_code_hash.toLowerCase(),'RPC_RUNTIME_HASH_DIVERGENCE');
    required(primary.owner.toLowerCase()===peer.owner.toLowerCase(),'RPC_OWNER_DIVERGENCE');
    required(primary.owner_match&&peer.owner_match,'OWNER_MISMATCH');
    required(primary.deployment_sender_match&&primary.deployment_contract_match&&primary.deployment_receipt_success,'DEPLOYMENT_LINEAGE_MISMATCH');
    evidence.status='IDENTITY_PROBED'; evidence.consensus_count=core.length; evidence.selected=primary; evidence.peer=peer;
    evidence.identity_conclusion=primary.hardened_source_hash_match?'MATCH_CURRENT_HARDENED_ARTIFACT':primary.historical_variant_matches.length?`MATCH_HISTORICAL_SOURCE_KEY:${primary.historical_variant_matches.join(',')}`:'MATCH_NEITHER_TESTED_ARTIFACT';
    evidence.deployed_runtime_summary={bytes:primary.executor_code_bytes,hash:primary.executor_code_hash};
  } else { evidence.consensus_count=core.length; evidence.block_reason='INSUFFICIENT_CORE_RPC_CONSENSUS'; }
  await fs.mkdir('evidence',{recursive:true});
  await fs.writeFile('evidence/p0a-runtime-identity.json',JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify(evidence,null,2));
  required(evidence.status==='IDENTITY_PROBED',evidence.block_reason||'RUNTIME_IDENTITY_PROBE_FAILED');
  required(evidence.identity_conclusion==='MATCH_CURRENT_HARDENED_ARTIFACT',`DEPLOYED_IDENTITY_IS_${evidence.identity_conclusion}`);
  console.log('P0-A runtime identity: PASS');
  console.log('No transaction was signed or broadcast.');
}
await main();