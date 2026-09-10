// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmSemantic {
    function addr(uint256 privateKey) external returns (address);
    function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);
    function expectRevert() external;
}

interface IExecutorCallbackTarget {
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns (bool);
    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory userData) external;
    function uniswapV3FlashCallback(uint256 fee0, uint256 fee1, bytes calldata data) external;
}

contract MockSemanticERC20 is IERC20 {
    mapping(address => uint256) internal balances;
    mapping(address => mapping(address => uint256)) internal allowances;
    function balanceOf(address account) external view override returns (uint256) { return balances[account]; }
    function transfer(address recipient, uint256 amount) external override returns (bool) {
        require(balances[msg.sender] >= amount, "balance");
        balances[msg.sender] -= amount;
        balances[recipient] += amount;
        return true;
    }
    function approve(address spender, uint256 amount) external override returns (bool) { allowances[msg.sender][spender] = amount; return true; }
}

contract MaliciousAavePool is IPool {
    function flashLoanSimple(address receiverAddress, address asset, uint256 amount, bytes calldata params, uint16) external override {
        PhantomX_Production_Executor.ExecutionIntent memory intent = abi.decode(params, (PhantomX_Production_Executor.ExecutionIntent));
        intent.routerA = address(0x9999999999999999999999999999999999999999);
        IExecutorCallbackTarget(receiverAddress).executeOperation(asset, amount, 0, receiverAddress, abi.encode(intent));
    }
}

contract SilentAavePool is IPool {
    function flashLoanSimple(address receiverAddress, address asset, uint256 amount, bytes calldata params, uint16) external override {
        IExecutorCallbackTarget(receiverAddress).executeOperation(asset, amount, 0, receiverAddress, params);
    }
}

contract MaliciousBalancerVault is IBalancerVault {
    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external override {
        PhantomX_Production_Executor.ExecutionIntent memory intent = abi.decode(userData, (PhantomX_Production_Executor.ExecutionIntent));
        intent.routerA = address(0x9999999999999999999999999999999999999999);
        address[] memory callbackTokens = new address[](1);
        callbackTokens[0] = tokens[0];
        uint256[] memory callbackAmounts = new uint256[](1);
        callbackAmounts[0] = amounts[0];
        uint256[] memory fees = new uint256[](1);
        fees[0] = 0;
        IExecutorCallbackTarget(recipient).receiveFlashLoan(callbackTokens, callbackAmounts, fees, abi.encode(intent));
    }
}

contract SilentBalancerVault is IBalancerVault {
    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external override {
        uint256[] memory fees = new uint256[](tokens.length);
        IExecutorCallbackTarget(recipient).receiveFlashLoan(tokens, amounts, fees, userData);
    }
}

contract MaliciousUniswapV3Pool is IUniswapV3Pool {
    address public token0Address;
    address public token1Address;

    constructor(address token0_, address token1_) { token0Address = token0_; token1Address = token1_; }
    function token0() external view override returns (address) { return token0Address; }
    function token1() external view override returns (address) { return token1Address; }
    function flash(address recipient, uint256, uint256, bytes calldata data) external override {
        PhantomX_Production_Executor.ExecutionIntent memory intent = abi.decode(data, (PhantomX_Production_Executor.ExecutionIntent));
        intent.routerA = address(0x9999999999999999999999999999999999999999);
        IExecutorCallbackTarget(recipient).uniswapV3FlashCallback(0, 0, abi.encode(intent));
    }
}

contract SilentUniswapV3Pool is IUniswapV3Pool {
    address public token0Address;
    address public token1Address;

    constructor(address token0_, address token1_) { token0Address = token0_; token1Address = token1_; }
    function token0() external view override returns (address) { return token0Address; }
    function token1() external view override returns (address) { return token1Address; }
    function flash(address recipient, uint256, uint256, bytes calldata data) external override {
        IExecutorCallbackTarget(recipient).uniswapV3FlashCallback(0, 0, data);
    }
}

contract PhantomXExecutorSemanticHarness is PhantomX_Production_Executor {
    constructor(address signer) { owner = signer; }
    function verify(ExecutionIntent memory intent) external view returns (bool) { return _verifyIntentSignature(intent); }
    function allowAave(address p) external { isAavePool[p] = true; }
    function allowBalancer(address p) external { isBalancerVault[p] = true; }
    function allowUniswapV3(address p) external { isUniswapV3Pool[p] = true; }
}

contract PhantomXExecutorSemanticHardeningTest {
    VmSemantic internal constant vm = VmSemantic(address(uint160(uint256(keccak256("hevm cheat code")))));
    uint256 internal constant PRIVATE_KEY = 0x0123456789012345678901234567890123456789012345678901234567890123;
    uint256 internal constant SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;
    address internal ownerAddress;
    PhantomXExecutorSemanticHarness internal executor;

    function setUp() public { ownerAddress = vm.addr(PRIVATE_KEY); executor = new PhantomXExecutorSemanticHarness(ownerAddress); }

    function _intent(PhantomX_Production_Executor.FlashProviderType provider, address providerAddress) internal view returns (PhantomX_Production_Executor.ExecutionIntent memory intent) {
        intent.executionId = keccak256(abi.encode("semantic-hardening", providerAddress));
        intent.providerType = provider;
        intent.providerAddress = providerAddress;
        intent.tokenBorrow = address(0x3333333333333333333333333333333333333333);
        intent.amountBorrow = 123456789;
        intent.swap1Type = PhantomX_Production_Executor.SwapType.V2;
        intent.routerA = address(0x4444444444444444444444444444444444444444);
        intent.pathA = hex"1234";
        intent.minAmountOut1 = 120000000;
        intent.swap2Type = PhantomX_Production_Executor.SwapType.V2;
        intent.routerB = address(0x5555555555555555555555555555555555555555);
        intent.pathB = hex"1234";
        intent.minAmountOutFinal = 125000000;
        intent.minimumOnChainSurplus = 500000;
        intent.maximumGasLimit = 5000000;
        intent.deadline = 2000000000;
    }

    function _structHash(PhantomX_Production_Executor.ExecutionIntent memory intent) internal pure returns (bytes32) {
        bytes32 typeHash = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
        bytes32[17] memory words;
        words[0] = typeHash; words[1] = intent.executionId; words[2] = bytes32(uint256(uint8(intent.providerType))); words[3] = bytes32(uint256(uint160(intent.providerAddress))); words[4] = bytes32(uint256(uint160(intent.tokenBorrow))); words[5] = bytes32(intent.amountBorrow); words[6] = bytes32(uint256(uint8(intent.swap1Type))); words[7] = bytes32(uint256(uint160(intent.routerA))); words[8] = keccak256(intent.pathA); words[9] = bytes32(intent.minAmountOut1); words[10] = bytes32(uint256(uint8(intent.swap2Type))); words[11] = bytes32(uint256(uint160(intent.routerB))); words[12] = keccak256(intent.pathB); words[13] = bytes32(intent.minAmountOutFinal); words[14] = bytes32(intent.minimumOnChainSurplus); words[15] = bytes32(intent.maximumGasLimit); words[16] = bytes32(intent.deadline);
        return keccak256(abi.encodePacked(words));
    }

    function _digest(PhantomX_Production_Executor.ExecutionIntent memory intent) internal view returns (bytes32) { return keccak256(abi.encodePacked(bytes2(0x1901), executor.DOMAIN_SEPARATOR(), _structHash(intent))); }

    function _signedIntent(PhantomX_Production_Executor.ExecutionIntent memory intent) internal returns (PhantomX_Production_Executor.ExecutionIntent memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        intent.signature = abi.encodePacked(r, s, v);
        return intent;
    }

    function test_rejects_high_s_signature() public {
        PhantomX_Production_Executor.ExecutionIntent memory intent = _intent(PhantomX_Production_Executor.FlashProviderType.AAVE, address(0x2222222222222222222222222222222222222222));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        bytes32 malleableS = bytes32(SECP256K1_N - uint256(s));
        uint8 malleableV = v == 27 ? 28 : 27;
        intent.signature = abi.encodePacked(r, malleableS, malleableV);
        vm.expectRevert();
        executor.verify(intent);
    }

    function test_rejects_invalid_signature_v() public {
        PhantomX_Production_Executor.ExecutionIntent memory intent = _intent(PhantomX_Production_Executor.FlashProviderType.AAVE, address(0x2222222222222222222222222222222222222222));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        v;
        intent.signature = abi.encodePacked(r, s, uint8(0));
        vm.expectRevert();
        executor.verify(intent);
    }

    function test_aave_callback_rejects_mutated_signed_intent() public {
        MaliciousAavePool provider = new MaliciousAavePool();
        executor.allowAave(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.AAVE, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_balancer_callback_rejects_mutated_signed_intent() public {
        MaliciousBalancerVault provider = new MaliciousBalancerVault();
        executor.allowBalancer(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.BALANCER, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_uniswap_v3_callback_rejects_mutated_signed_intent() public {
        address borrowToken = address(0x3333333333333333333333333333333333333333);
        MaliciousUniswapV3Pool provider = new MaliciousUniswapV3Pool(borrowToken, address(0x6666666666666666666666666666666666666666));
        executor.allowUniswapV3(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.UNISWAP_V3, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_aave_callback_rejects_missing_flash_transfer() public {
        MockSemanticERC20 token = new MockSemanticERC20();
        SilentAavePool provider = new SilentAavePool();
        executor.allowAave(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.AAVE, address(provider)));
        intent.tokenBorrow = address(token);
        intent = _signedIntent(intent);
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_balancer_callback_rejects_missing_flash_transfer() public {
        MockSemanticERC20 token = new MockSemanticERC20();
        SilentBalancerVault provider = new SilentBalancerVault();
        executor.allowBalancer(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.BALANCER, address(provider)));
        intent.tokenBorrow = address(token);
        intent = _signedIntent(intent);
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_uniswap_v3_callback_rejects_missing_flash_transfer() public {
        MockSemanticERC20 token = new MockSemanticERC20();
        SilentUniswapV3Pool provider = new SilentUniswapV3Pool(address(token), address(0x6666666666666666666666666666666666666666));
        executor.allowUniswapV3(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signedIntent(_intent(PhantomX_Production_Executor.FlashProviderType.UNISWAP_V3, address(provider)));
        intent.tokenBorrow = address(token);
        intent = _signedIntent(intent);
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }
}
