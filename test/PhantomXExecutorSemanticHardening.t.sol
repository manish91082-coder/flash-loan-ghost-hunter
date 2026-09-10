// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmSemantic {
    function addr(uint256 privateKey) external returns (address);
    function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);
    function expectRevert() external;
}

contract PhantomXExecutorSemanticHarness is PhantomX_Production_Executor {
    constructor(address signer) { owner = signer; }
    function verify(ExecutionIntent memory intent) external view returns (bool) { return _verifyIntentSignature(intent); }
}

contract PhantomXExecutorSemanticHardeningTest {
    VmSemantic internal constant vm = VmSemantic(address(uint160(uint256(keccak256("hevm cheat code")))));
    uint256 internal constant PRIVATE_KEY = 0x0123456789012345678901234567890123456789012345678901234567890123;
    address internal ownerAddress;
    PhantomXExecutorSemanticHarness internal executor;

    function setUp() public { ownerAddress = vm.addr(PRIVATE_KEY); executor = new PhantomXExecutorSemanticHarness(ownerAddress); }

    function _intent() internal view returns (PhantomX_Production_Executor.ExecutionIntent memory intent) {
        intent.executionId = keccak256("semantic-hardening");
        intent.providerType = PhantomX_Production_Executor.FlashProviderType.AAVE;
        intent.providerAddress = address(0x2222222222222222222222222222222222222222);
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
        intent.maximumGasLimit = 500000;
        intent.deadline = 2000000000;
    }

    function _structHash(PhantomX_Production_Executor.ExecutionIntent memory intent) internal pure returns (bytes32) {
        bytes32 typeHash = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
        bytes32[17] memory words;
        words[0] = typeHash; words[1] = intent.executionId; words[2] = bytes32(uint256(uint8(intent.providerType))); words[3] = bytes32(uint256(uint160(intent.providerAddress))); words[4] = bytes32(uint256(uint160(intent.tokenBorrow))); words[5] = bytes32(intent.amountBorrow); words[6] = bytes32(uint256(uint8(intent.swap1Type))); words[7] = bytes32(uint256(uint160(intent.routerA))); words[8] = keccak256(intent.pathA); words[9] = bytes32(intent.minAmountOut1); words[10] = bytes32(uint256(uint8(intent.swap2Type))); words[11] = bytes32(uint256(uint160(intent.routerB))); words[12] = keccak256(intent.pathB); words[13] = bytes32(intent.minAmountOutFinal); words[14] = bytes32(intent.minimumOnChainSurplus); words[15] = bytes32(intent.maximumGasLimit); words[16] = bytes32(intent.deadline);
        return keccak256(abi.encodePacked(words));
    }

    function _digest(PhantomX_Production_Executor.ExecutionIntent memory intent) internal view returns (bytes32) { return keccak256(abi.encodePacked(bytes2(0x1901), executor.DOMAIN_SEPARATOR(), _structHash(intent))); }

    function test_rejects_high_s_signature() public {
        PhantomX_Production_Executor.ExecutionIntent memory intent = _intent();
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        bytes32 malleableS = bytes32(type(uint256).max - uint256(s) + 1);
        uint8 malleableV = v == 27 ? 28 : 27;
        intent.signature = abi.encodePacked(r, malleableS, malleableV);
        vm.expectRevert();
        executor.verify(intent);
    }

    function test_rejects_invalid_signature_v() public {
        PhantomX_Production_Executor.ExecutionIntent memory intent = _intent();
        (uint8 unusedV, bytes32 r, bytes32 s) = vm.sign(PRIVATE_KEY, _digest(intent));
        unusedV;
        intent.signature = abi.encodePacked(r, s, uint8(0));
        vm.expectRevert();
        executor.verify(intent);
    }
}
