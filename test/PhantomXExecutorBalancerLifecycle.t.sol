// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmBalancer {
    function addr(uint256 privateKey) external returns (address);
    function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);
    function expectRevert() external;
}

interface IERC20TransferFrom is IERC20 { function transferFrom(address sender, address recipient, uint256 amount) external returns (bool); }
interface IExecutorBalancerTarget { function executeOpportunity(PhantomX_Production_Executor.ExecutionIntent memory intent) external; function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory userData) external; }

contract MockBalancerToken is IERC20TransferFrom {
    mapping(address => uint256) internal balances;
    mapping(address => mapping(address => uint256)) internal allowances;
    function balanceOf(address account) external view override returns (uint256) { return balances[account]; }
    function transfer(address recipient, uint256 amount) external override returns (bool) { require(balances[msg.sender] >= amount, "balance"); balances[msg.sender] -= amount; balances[recipient] += amount; return true; }
    function transferFrom(address sender, address recipient, uint256 amount) external override returns (bool) { uint256 a = allowances[sender][msg.sender]; require(a >= amount, "allowance"); require(balances[sender] >= amount, "balance"); allowances[sender][msg.sender] = a - amount; balances[sender] -= amount; balances[recipient] += amount; return true; }
    function approve(address spender, uint256 amount) external override returns (bool) { allowances[msg.sender][spender] = amount; return true; }
    function mint(address recipient, uint256 amount) external { balances[recipient] += amount; }
}

contract MockBalancerProfitRouter is IUniswapV2Router {
    uint256 public immutable bonus;
    constructor(uint256 bonus_) { bonus = bonus_; }
    function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint) external override returns (uint[] memory amounts) {
        require(path.length == 2, "path");
        IERC20TransferFrom(path[0]).transferFrom(msg.sender, address(this), amountIn);
        uint256 out = amountIn + bonus;
        require(out >= amountOutMin, "minOut");
        MockBalancerToken(path[1]).mint(to, out);
        amounts = new uint[](2); amounts[0] = amountIn; amounts[1] = out;
    }
}

contract RealisticBalancerVaultMock is IBalancerVault {
    uint256 public immutable fee;
    bool public attemptReentry;
    bool public reentryAttempted;
    bool public reentryRejected;
    bytes32 public reentryRevertHash;
    bool public lendAssets = true;
    uint256 public lastRepayment;
    uint256 public callbackCount;
    address public immutable executor;

    constructor(uint256 fee_, address executor_) { fee = fee_; executor = executor_; }
    function setAttemptReentry(bool enabled) external { attemptReentry = enabled; }
    function setLendAssets(bool enabled) external { lendAssets = enabled; }

    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external override {
        require(tokens.length == 1 && amounts.length == 1, "mock shape");
        if (lendAssets) MockBalancerToken(tokens[0]).mint(recipient, amounts[0]);
        uint256 beforeBalance = MockBalancerToken(tokens[0]).balanceOf(address(this));
        if (attemptReentry) {
            reentryAttempted = true;
            PhantomX_Production_Executor.ExecutionIntent memory emptyIntent;
            (bool ok, bytes memory data) = executor.call(abi.encodeCall(IExecutorBalancerTarget.executeOpportunity, (emptyIntent)));
            reentryRejected = !ok;
            reentryRevertHash = keccak256(data);
        }
        address[] memory callbackTokens = new address[](1);
        uint256[] memory callbackAmounts = new uint256[](1);
        uint256[] memory callbackFees = new uint256[](1);
        callbackTokens[0] = tokens[0]; callbackAmounts[0] = amounts[0]; callbackFees[0] = fee;
        callbackCount += 1;
        IExecutorBalancerTarget(recipient).receiveFlashLoan(callbackTokens, callbackAmounts, callbackFees, userData);
        uint256 afterBalance = MockBalancerToken(tokens[0]).balanceOf(address(this));
        lastRepayment = afterBalance - beforeBalance;
        require(lastRepayment == amounts[0] + fee, "exact repayment missing");
    }
}

contract PhantomXBalancerLifecycleHarness is PhantomX_Production_Executor {
    constructor(address signer) { owner = signer; }
    function allowBalancer(address p) external { isBalancerVault[p] = true; }
    function allowRouter(address r) external { allowedRouters[r] = true; }
    function allowToken(address t) external { allowedTokens[t] = true; }
}

contract PhantomXExecutorBalancerLifecycleTest {
    VmBalancer internal constant vm = VmBalancer(address(uint160(uint256(keccak256("hevm cheat code")))));
    uint256 internal constant PRIVATE_KEY = 0x0123456789012345678901234567890123456789012345678901234567890123;
    address internal signer;
    PhantomXBalancerLifecycleHarness internal executor;
    MockBalancerToken internal borrow;
    MockBalancerToken internal mid;
    MockBalancerProfitRouter internal routerA;
    MockBalancerProfitRouter internal routerB;
    RealisticBalancerVaultMock internal vault;

    function setUp() public {
        signer = vm.addr(PRIVATE_KEY);
        executor = new PhantomXBalancerLifecycleHarness(signer);
        borrow = new MockBalancerToken(); mid = new MockBalancerToken();
        routerA = new MockBalancerProfitRouter(100); routerB = new MockBalancerProfitRouter(100);
        vault = new RealisticBalancerVaultMock(7, address(executor));
        executor.allowBalancer(address(vault)); executor.allowRouter(address(routerA)); executor.allowRouter(address(routerB));
        executor.allowToken(address(borrow)); executor.allowToken(address(mid));
    }

    function _structHash(PhantomX_Production_Executor.ExecutionIntent memory intent) internal pure returns (bytes32) {
        bytes32 typeHash = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
        bytes32[17] memory w;
        w[0]=typeHash; w[1]=intent.executionId; w[2]=bytes32(uint256(uint8(intent.providerType))); w[3]=bytes32(uint256(uint160(intent.providerAddress))); w[4]=bytes32(uint256(uint160(intent.tokenBorrow))); w[5]=bytes32(intent.amountBorrow);
        w[6]=bytes32(uint256(uint8(intent.swap1Type))); w[7]=bytes32(uint256(uint160(intent.routerA))); w[8]=keccak256(intent.pathA); w[9]=bytes32(intent.minAmountOut1); w[10]=bytes32(uint256(uint8(intent.swap2Type))); w[11]=bytes32(uint256(uint160(intent.routerB))); w[12]=keccak256(intent.pathB); w[13]=bytes32(intent.minAmountOutFinal); w[14]=bytes32(intent.minimumOnChainSurplus); w[15]=bytes32(intent.maximumGasLimit); w[16]=bytes32(intent.deadline);
        return keccak256(abi.encodePacked(w));
    }
    function _digest(PhantomX_Production_Executor.ExecutionIntent memory intent) internal view returns (bytes32) { return keccak256(abi.encodePacked(bytes2(0x1901), executor.DOMAIN_SEPARATOR(), _structHash(intent))); }

    function _signed(uint256 amount, uint256 surplus) internal returns (PhantomX_Production_Executor.ExecutionIntent memory intent) {
        address[] memory pathA = new address[](2); pathA[0]=address(borrow); pathA[1]=address(mid);
        address[] memory pathB = new address[](2); pathB[0]=address(mid); pathB[1]=address(borrow);
        intent.executionId=keccak256(abi.encode("balancer-lifecycle",address(vault),amount,surplus)); intent.providerType=PhantomX_Production_Executor.FlashProviderType.BALANCER; intent.providerAddress=address(vault); intent.tokenBorrow=address(borrow); intent.amountBorrow=amount;
        intent.swap1Type=PhantomX_Production_Executor.SwapType.V2; intent.routerA=address(routerA); intent.pathA=abi.encode(pathA); intent.minAmountOut1=amount;
        intent.swap2Type=PhantomX_Production_Executor.SwapType.V2; intent.routerB=address(routerB); intent.pathB=abi.encode(pathB); intent.minAmountOutFinal=amount+7+surplus; intent.minimumOnChainSurplus=surplus; intent.maximumGasLimit=5_000_000; intent.deadline=2_000_000_000;
        (uint8 v,bytes32 r,bytes32 s)=vm.sign(PRIVATE_KEY,_digest(intent)); intent.signature=abi.encodePacked(r,s,v);
    }

    function test_balancer_exact_repayment_and_state_cleanup() public {
        uint256 amount=1_000_000; uint256 surplus=50; PhantomX_Production_Executor.ExecutionIntent memory intent=_signed(amount,surplus); uint256 vaultBefore=borrow.balanceOf(address(vault));
        executor.executeOpportunity(intent);
        require(vault.callbackCount()==1,"callback missing"); require(vault.lastRepayment()==amount+7,"wrong repayment amount"); require(borrow.balanceOf(address(vault))==vaultBefore+amount+7,"vault balance mismatch"); require(executor.activeExecutionId()==bytes32(0),"active execution leaked");
    }

    function test_balancer_rejects_missing_borrowed_asset_and_clears_state() public {
        vault.setLendAssets(false); PhantomX_Production_Executor.ExecutionIntent memory intent=_signed(1_000_000,0); vm.expectRevert(); executor.executeOpportunity(intent); require(executor.activeExecutionId()==bytes32(0),"active execution leaked");
    }

    function test_balancer_reentrancy_is_rejected() public {
        vault.setAttemptReentry(true); PhantomX_Production_Executor.ExecutionIntent memory intent=_signed(1_000_000,50); executor.executeOpportunity(intent); require(vault.reentryAttempted(),"reentry not attempted"); require(vault.reentryRejected(),"reentry not rejected"); require(vault.reentryRevertHash()!=bytes32(0),"missing reentry evidence"); require(executor.activeExecutionId()==bytes32(0),"active execution leaked after reentry");
    }
}
