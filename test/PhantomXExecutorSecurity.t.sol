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

    function _validV2Params() internal view returns (bytes memory) {
        address[] memory leg1 = new address[](2);
        leg1[0] = BORROW;
        leg1[1] = MID;
        address[] memory leg2 = new address[](2);
        leg2[0] = MID;
        leg2[1] = BORROW;
        return _params(abi.encode(leg1), abi.encode(leg2), 0);
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

    function test_callback_rejects_wrong_initiator() public {
        vm.expectRevert();
        provider.callAaveCallback(
            executor,
            BORROW,
            1e6,
            0,
            address(0xDEAD),
            _validV2Params()
        );
    }

    function test_callback_rejects_wrong_asset() public {
        vm.expectRevert();
        provider.callAaveCallback(
            executor,
            BAD,
            1e6,
            0,
            address(executor),
            _validV2Params()
        );
    }

    function test_callback_rejects_wrong_amount() public {
        vm.expectRevert();
        provider.callAaveCallback(
            executor,
            BORROW,
            2e6,
            0,
            address(executor),
            _validV2Params()
        );
    }

    function test_callback_rejects_wrong_provider_type() public {
        bytes memory params = abi.encode(
            executionId,
            uint8(2),
            address(provider),
            BORROW,
            uint256(1e6),
            uint8(0),
            ROUTER_A,
            _validV2Path(BORROW, MID),
            uint256(1),
            uint8(0),
            ROUTER_B,
            _validV2Path(MID, BORROW),
            uint256(1),
            uint256(0),
            uint256(5_000_000),
            block.timestamp + 1_000,
            bytes("")
        );
        vm.expectRevert();
        provider.callAaveCallback(executor, BORROW, 1e6, 0, address(executor), params);
    }

    function test_callback_rejects_stale_execution_id() public {
        bytes32 staleId = keccak256("stale-execution");
        address[] memory leg1 = new address[](2);
        leg1[0] = BORROW;
        leg1[1] = MID;
        address[] memory leg2 = new address[](2);
        leg2[0] = MID;
        leg2[1] = BORROW;
        bytes memory params = abi.encode(
            staleId,
            uint8(0),
            address(provider),
            BORROW,
            uint256(1e6),
            uint8(0),
            ROUTER_A,
            abi.encode(leg1),
            uint256(1),
            uint8(0),
            ROUTER_B,
            abi.encode(leg2),
            uint256(1),
            uint256(0),
            uint256(5_000_000),
            block.timestamp + 1_000,
            bytes("")
        );
        vm.expectRevert();
        provider.callAaveCallback(executor, BORROW, 1e6, 0, address(executor), params);
    }

    function _validV2Path(address tokenIn, address tokenOut) internal pure returns (bytes memory) {
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        return abi.encode(path);
    }
}
