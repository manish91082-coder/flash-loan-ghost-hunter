// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface Vm {
    function store(address target, bytes32 slot, bytes32 value) external;
    function expectRevert() external;
}

contract MockCaller {
    function callAaveCallback(
        PhantomX_Production_Executor executor,
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        return executor.executeOperation(asset, amount, premium, initiator, params);
    }
}

contract PhantomXExecutorSecurityTest {
    Vm internal constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    address internal constant BORROW = address(0x1001);
    address internal constant MID = address(0x1002);
    address internal constant FINAL = address(0x1003);
    address internal constant BAD = address(0xBADD);
    address internal constant ROUTER_A = address(0x2001);
    address internal constant ROUTER_B = address(0x2002);

    PhantomX_Production_Executor internal executor;
    MockCaller internal provider;
    bytes32 internal executionId = keccak256("executor-security-test");

    function setUp() public {
        executor = new PhantomX_Production_Executor();
        provider = new MockCaller();
        executor.setAavePool(address(provider), true);
        executor.setRouter(ROUTER_A, true);
        executor.setRouter(ROUTER_B, true);
        executor.setToken(BORROW, true);
        executor.setToken(MID, true);
        executor.setToken(FINAL, true);
        vm.store(address(executor), bytes32(uint256(10)), executionId);
    }

    function _params(bytes memory pathA, bytes memory pathB, uint8 swapType) internal view returns (bytes memory) {
        return abi.encode(
            executionId,
            uint8(0),
            address(provider),
            BORROW,
            uint256(1e6),
            swapType,
            ROUTER_A,
            pathA,
            uint256(1),
            uint8(0),
            ROUTER_B,
            pathB,
            uint256(1),
            uint256(0),
            uint256(5_000_000),
            block.timestamp + 1_000,
            bytes("")
        );
    }

    function test_v2_intermediate_token_must_be_allowlisted() public {
        address[] memory leg1 = new address[](3);
        leg1[0] = BORROW;
        leg1[1] = BAD;
        leg1[2] = MID;
        address[] memory leg2 = new address[](2);
        leg2[0] = MID;
        leg2[1] = BORROW;

        vm.expectRevert();
        provider.callAaveCallback(
            executor,
            BORROW,
            1e6,
            0,
            address(executor),
            _params(abi.encode(leg1), abi.encode(leg2), 0)
        );
    }

    function test_v3_intermediate_token_must_be_allowlisted() public {
        bytes memory leg1 = abi.encodePacked(BORROW, uint24(3000), BAD, uint24(3000), MID);
        bytes memory leg2 = abi.encodePacked(MID, uint24(3000), BORROW);

        vm.expectRevert();
        provider.callAaveCallback(
            executor,
            BORROW,
            1e6,
            0,
            address(executor),
            _params(leg1, leg2, 1)
        );
    }

    function test_callback_rejects_untrusted_provider() public {
        vm.expectRevert();
        executor.executeOperation(
            BORROW,
            1e6,
            0,
            address(executor),
            ""
        );
    }
}
