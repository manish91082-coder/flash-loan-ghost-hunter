// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmAaveHardening {
    function addr(uint256 privateKey) external returns (address);
    function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);
    function expectRevert(bytes calldata reason) external;
}

contract AaveHardeningMockERC20 is IERC20 {
    mapping(address => uint256) internal balances;
    mapping(address => mapping(address => uint256)) internal allowances;

    function balanceOf(address account) external view override returns (uint256) { return balances[account]; }
    function allowance(address owner_, address spender) external view returns (uint256) { return allowances[owner_][spender]; }
    function transfer(address recipient, uint256 amount) external override returns (bool) {
        require(balances[msg.sender] >= amount, "balance");
        balances[msg.sender] -= amount;
        balances[recipient] += amount;
        return true;
    }
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool) {
        require(balances[sender] >= amount, "balance");
        uint256 current = allowances[sender][msg.sender];
        require(current >= amount, "allowance");
        allowances[sender][msg.sender] = current - amount;
        balances[sender] -= amount;
        balances[recipient] += amount;
        return true;
    }
    function approve(address spender, uint256 amount) external override returns (bool) { allowances[msg.sender][spender] = amount; return true; }
    function mint(address recipient, uint256 amount) external { balances[recipient] += amount; }
}

contract AaveHardeningMockV2Router is IUniswapV2Router {
    uint256 public immutable outputAmount;
    constructor(uint256 output_) { outputAmount = output_; }
    function swapExactTokensForTokens(uint amountIn, uint, address[] calldata path, address to, uint) external override returns (uint[] memory amounts) {
        require(path.length >= 2, "path");
        AaveHardeningMockERC20(path[0]).transferFrom(msg.sender, address(this), amountIn);
        AaveHardeningMockERC20(path[path.length - 1]).mint(to, outputAmount);
        amounts = new uint[](2);
        amounts[0] = amountIn;
        amounts[1] = outputAmount;
    }
}

contract AaveHardeningMockProvider is IPool {
    uint256 public immutable premium;
    bool public immutable underPull;
    uint256 public lastRepayment;
    uint256 public allowanceSeenBeforePull;

    constructor(uint256 premium_, bool underPull_) {
        premium = premium_;
        underPull = underPull_;
    }

    function flashLoanSimple(address receiverAddress, address asset, uint256 amount, bytes calldata params, uint16) external override {
        AaveHardeningMockERC20(asset).mint(receiverAddress, amount);
        bool callbackOk = IExecutorAaveHardeningCallback(receiverAddress).executeOperation(asset, amount, premium, receiverAddress, params);
        require(callbackOk, "callback");

        uint256 due = amount + premium;
        allowanceSeenBeforePull = AaveHardeningMockERC20(asset).allowance(receiverAddress, address(this));
        require(allowanceSeenBeforePull == due, "incorrect repayment allowance");
        uint256 pullAmount = underPull ? due - 1 : due;
        bool pulled = AaveHardeningMockERC20(asset).transferFrom(receiverAddress, address(this), pullAmount);
        require(pulled, "repayment pull");
        lastRepayment = pullAmount;
    }
}

interface IExecutorAaveHardeningCallback {
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns(bool);
}

contract PhantomXExecutorAaveHardeningHarness is PhantomX_Production_Executor {
    constructor(address signer) { owner = signer; }
    function allowAave(address provider) external { isAavePool[provider] = true; }
    function allowRouter(address router) external { allowedRouters[router] = true; }
    function allowToken(address token) external { allowedTokens[token] = true; }
}

contract PhantomXExecutorAaveRepaymentHardeningTest {
    VmAaveHardening internal constant vm = VmAaveHardening(address(uint160(uint256(keccak256("hevm cheat code")))));
    uint256 internal constant PRIVATE_KEY = 0x0123456789012345678901234567890123456789012345678901234567890123;
    address internal signer;
    AaveHardeningMockERC20 internal borrowToken;
    AaveHardeningMockERC20 internal midToken;
    AaveHardeningMockV2Router internal routerA;
    AaveHardeningMockV2Router internal routerB;

    function _newExecutor(AaveHardeningMockProvider provider) internal returns (PhantomXExecutorAaveHardeningHarness executor) {
        executor = new PhantomXExecutorAaveHardeningHarness(signer);
        executor.allowAave(address(provider));
        executor.allowRouter(address(routerA));
        executor.allowRouter(address(routerB));
        executor.allowToken(address(borrowToken));
        executor.allowToken(address(midToken));
    }

    function setUp() public {
        signer = vm.addr(PRIVATE_KEY);
        borrowToken = new AaveHardeningMockERC20();
        midToken = new AaveHardeningMockERC20();
        routerA = new AaveHardeningMockV2Router(100);
        routerB = new AaveHardeningMockV2Router(107);
    }

    function _structHash(PhantomX_Production_Executor.ExecutionIntent memory intent) internal pure returns(bytes32) {
        bytes32 typeHash = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
        bytes32[17] memory w;
        w[0] = typeHash;
        w[1] = intent.executionId;
        w[2] = bytes32(uint256(uint8(intent.providerType)));
        w[3] = bytes32(uint256(uint160(intent.providerAddress)));
        w[4] = bytes32(uint256(uint160(intent.tokenBorrow)));
        w[5] = bytes32(intent.amountBorrow);
        w[6] = bytes32(uint256(uint8(intent.swap1Type)));
        w[7] = bytes32(uint256(uint160(intent.routerA)));
        w[8] = keccak256(intent.pathA);
        w[9] = bytes32(intent.minAmountOut1);
        w[10] = bytes32(uint256(uint8(intent.swap2Type)));
        w[11] = bytes32(uint256(uint160(intent.routerB)));
        w[12] = keccak256(intent.pathB);
        w[13] = bytes32(intent.minAmountOutFinal);
        w[14] = bytes32(intent.minimumOnChainSurplus);
        w[15] = bytes32(intent.maximumGasLimit);
        w[16] = bytes32(intent.deadline);
        return keccak256(abi.encodePacked(w));
    }

    function _digest(PhantomX_Production_Executor.ExecutionIntent memory intent) internal view returns(bytes32) {
        return keccak256(abi.encodePacked(bytes2(0x1901), PhantomXExecutorAaveHardeningHarness(payable(msg.sender)).DOMAIN_SEPARATOR(), _structHash(intent)));
    }

    function _signed(PhantomX_Production_Executor.ExecutionIntent memory intent, PhantomXExecutorAaveHardeningHarness executor) internal returns(PhantomX_Production_Executor.ExecutionIntent memory) {
        bytes32 digest = keccak256(abi.encodePacked(bytes2(0x1901), executor.DOMAIN_SEPARATOR(), _structHash(intent)));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, digest);
        intent.signature = abi.encodePacked(r, s, v);
        return intent;
    }

    function _intent(PhantomXExecutorAaveHardeningHarness executor, AaveHardeningMockProvider provider) internal view returns (PhantomX_Production_Executor.ExecutionIntent memory i) {
        address[] memory pathA = new address[](2);
        pathA[0] = address(borrowToken);
        pathA[1] = address(midToken);
        address[] memory pathB = new address[](2);
        pathB[0] = address(midToken);
        pathB[1] = address(borrowToken);

        i.executionId = keccak256(abi.encode("aave-repayment-hardening", address(provider), address(executor)));
        i.providerType = PhantomX_Production_Executor.FlashProviderType.AAVE;
        i.providerAddress = address(provider);
        i.tokenBorrow = address(borrowToken);
        i.amountBorrow = 100;
        i.swap1Type = PhantomX_Production_Executor.SwapType.V2;
        i.routerA = address(routerA);
        i.pathA = abi.encode(pathA);
        i.minAmountOut1 = 100;
        i.swap2Type = PhantomX_Production_Executor.SwapType.V2;
        i.routerB = address(routerB);
        i.pathB = abi.encode(pathB);
        i.minAmountOutFinal = 107;
        i.minimumOnChainSurplus = 0;
        i.maximumGasLimit = 5_000_000;
        i.deadline = 2_000_000_000;
    }

    function test_aave_exact_repayment_and_allowance_cleanup() public {
        AaveHardeningMockProvider provider = new AaveHardeningMockProvider(7, false);
        PhantomXExecutorAaveHardeningHarness executor = _newExecutor(provider);
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signed(_intent(executor, provider), executor);

        executor.executeOpportunity(intent);

        require(provider.lastRepayment() == 107, "incorrect repayment amount");
        require(provider.allowanceSeenBeforePull() == 107, "provider did not receive exact repayment allowance");
        require(borrowToken.allowance(address(executor), address(provider)) == 0, "Aave allowance not cleaned");
        require(executor.activeExecutionId() == bytes32(0), "active execution leaked");
    }

    function test_aave_under_repayment_is_rejected_after_provider_return() public {
        AaveHardeningMockProvider provider = new AaveHardeningMockProvider(7, true);
        PhantomXExecutorAaveHardeningHarness executor = _newExecutor(provider);
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signed(_intent(executor, provider), executor);

        vm.expectRevert(bytes("Aave repayment balance mismatch"));
        executor.executeOpportunity(intent);
    }
}
