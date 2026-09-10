// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmInvocation {
    function addr(uint256 privateKey) external returns (address);
    function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);
    function expectRevert() external;
}

interface IExecutorInvocationTarget {
    function executeOpportunity(PhantomX_Production_Executor.ExecutionIntent memory intent) external;
}

contract SilentAaveProviderInvocation is IPool {
    function flashLoanSimple(address, address, uint256, bytes calldata, uint16) external override {
        // Deliberately returns without calling executeOperation.
    }
}

contract SilentBalancerProviderInvocation is IBalancerVault {
    function flashLoan(address, address[] memory, uint256[] memory, bytes memory) external override {
        // Deliberately returns without calling receiveFlashLoan.
    }
}

contract SilentUniswapV3ProviderInvocation is IUniswapV3Pool {
    address public token0Address;
    address public token1Address;

    constructor(address token0_, address token1_) {
        token0Address = token0_;
        token1Address = token1_;
    }

    function token0() external view override returns (address) { return token0Address; }
    function token1() external view override returns (address) { return token1Address; }

    function flash(address, uint256, uint256, bytes calldata) external override {
        // Deliberately returns without calling uniswapV3FlashCallback.
    }
}

contract PhantomXExecutorCallbackInvocationHarness is PhantomX_Production_Executor {
    constructor(address signer) { owner = signer; }
    function allowAave(address p) external { isAavePool[p] = true; }
    function allowBalancer(address p) external { isBalancerVault[p] = true; }
    function allowUniswapV3(address p) external { isUniswapV3Pool[p] = true; }
}

contract PhantomXExecutorCallbackInvocationTest {
    VmInvocation internal constant vm = VmInvocation(address(uint160(uint256(keccak256("hevm cheat code")))));
    uint256 internal constant PRIVATE_KEY = 0x0123456789012345678901234567890123456789012345678901234567890123;
    address internal signer;
    PhantomXExecutorCallbackInvocationHarness internal executor;

    function setUp() public {
        signer = vm.addr(PRIVATE_KEY);
        executor = new PhantomXExecutorCallbackInvocationHarness(signer);
    }

    function _structHash(PhantomX_Production_Executor.ExecutionIntent memory intent) internal pure returns (bytes32) {
        bytes32 typeHash = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
        bytes32[17] memory words;
        words[0] = typeHash;
        words[1] = intent.executionId;
        words[2] = bytes32(uint256(uint8(intent.providerType)));
        words[3] = bytes32(uint256(uint160(intent.providerAddress)));
        words[4] = bytes32(uint256(uint160(intent.tokenBorrow)));
        words[5] = bytes32(intent.amountBorrow);
        words[6] = bytes32(uint256(uint8(intent.swap1Type)));
        words[7] = bytes32(uint256(uint160(intent.routerA)));
        words[8] = keccak256(intent.pathA);
        words[9] = bytes32(intent.minAmountOut1);
        words[10] = bytes32(uint256(uint8(intent.swap2Type)));
        words[11] = bytes32(uint256(uint160(intent.routerB)));
        words[12] = keccak256(intent.pathB);
        words[13] = bytes32(intent.minAmountOutFinal);
        words[14] = bytes32(intent.minimumOnChainSurplus);
        words[15] = bytes32(intent.maximumGasLimit);
        words[16] = bytes32(intent.deadline);
        return keccak256(abi.encodePacked(words));
    }

    function _digest(PhantomX_Production_Executor.ExecutionIntent memory intent) internal view returns (bytes32) {
        return keccak256(abi.encodePacked(bytes2(0x1901), executor.DOMAIN_SEPARATOR(), _structHash(intent)));
    }

    function _signed(PhantomX_Production_Executor.ExecutionIntent memory intent) internal returns (PhantomX_Production_Executor.ExecutionIntent memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        intent.signature = abi.encodePacked(r, s, v);
        return intent;
    }

    function _intent(PhantomX_Production_Executor.FlashProviderType providerType, address provider) internal view returns (PhantomX_Production_Executor.ExecutionIntent memory intent) {
        intent.executionId = keccak256(abi.encode("callback-invocation", provider));
        intent.providerType = providerType;
        intent.providerAddress = provider;
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

    function test_aave_provider_must_invoke_callback() public {
        SilentAaveProviderInvocation provider = new SilentAaveProviderInvocation();
        executor.allowAave(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signed(_intent(PhantomX_Production_Executor.FlashProviderType.AAVE, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_balancer_provider_must_invoke_callback() public {
        SilentBalancerProviderInvocation provider = new SilentBalancerProviderInvocation();
        executor.allowBalancer(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signed(_intent(PhantomX_Production_Executor.FlashProviderType.BALANCER, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }

    function test_uniswap_v3_provider_must_invoke_callback() public {
        address token0 = address(0x3333333333333333333333333333333333333333);
        address token1 = address(0x6666666666666666666666666666666666666666);
        SilentUniswapV3ProviderInvocation provider = new SilentUniswapV3ProviderInvocation(token0, token1);
        executor.allowUniswapV3(address(provider));
        PhantomX_Production_Executor.ExecutionIntent memory intent = _signed(_intent(PhantomX_Production_Executor.FlashProviderType.UNISWAP_V3, address(provider)));
        vm.expectRevert();
        executor.executeOpportunity(intent);
    }
}
