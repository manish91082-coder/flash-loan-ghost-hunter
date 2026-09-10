// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../contracts/PhantomX_Production_Executor.sol";

interface VmMatrix {
    function store(address target, bytes32 slot, bytes32 value) external;
    function expectRevert() external;
}

contract MockBalancerCaller {
    function callCallback(
        PhantomX_Production_Executor executor,
        address[] calldata tokens,
        uint256[] calldata amounts,
        uint256[] calldata fees,
        bytes calldata data
    ) external {
        executor.receiveFlashLoan(tokens, amounts, fees, data);
    }
}

contract MockV3Pool {
    address public token0;
    address public token1;

    constructor(address _token0, address _token1) {
        token0 = _token0;
        token1 = _token1;
    }

    function callCallback(
        PhantomX_Production_Executor executor,
        uint256 fee0,
        uint256 fee1,
        bytes calldata data
    ) external {
        executor.uniswapV3FlashCallback(fee0, fee1, data);
    }
}

contract PhantomXExecutorCallbackMatrixTest {
    VmMatrix internal constant vm = VmMatrix(address(uint160(uint256(keccak256("hevm cheat code")))));

    address internal constant BORROW = address(0x1001);
    address internal constant MID = address(0x1002);
    address internal constant BAD = address(0xBADD);
    address internal constant ROUTER_A = address(0x2001);
    address internal constant ROUTER_B = address(0x2002);

    PhantomX_Production_Executor internal executor;
    MockBalancerCaller internal balancer;
    MockV3Pool internal pool;
    bytes32 internal executionId = keccak256("callback-matrix");

    function setUp() public {
        executor = new PhantomX_Production_Executor();
        balancer = new MockBalancerCaller();
        pool = new MockV3Pool(BORROW, MID);

        executor.setBalancerVault(address(balancer), true);
        executor.setUniswapV3Pool(address(pool), true);
        executor.setRouter(ROUTER_A, true);
        executor.setRouter(ROUTER_B, true);
        executor.setToken(BORROW, true);
        executor.setToken(MID, true);
        vm.store(address(executor), bytes32(uint256(10)), executionId);
    }

    function _data(uint8 providerType, address provider, address tokenBorrow) internal view returns (bytes memory) {
        return abi.encode(
            executionId,
            providerType,
            provider,
            tokenBorrow,
            uint256(1e6),
            uint8(0),
            ROUTER_A,
            _path(tokenBorrow, MID),
            uint256(1),
            uint8(0),
            ROUTER_B,
            _path(MID, tokenBorrow),
            uint256(1),
            uint256(0),
            uint256(5_000_000),
            block.timestamp + 1_000,
            bytes("")
        );
    }

    function _path(address a, address b) internal pure returns (bytes memory) {
        address[] memory p = new address[](2);
        p[0] = a;
        p[1] = b;
        return abi.encode(p);
    }

    function _one(address token, uint256 amount) internal pure returns (address[] memory tokens, uint256[] memory amounts, uint256[] memory fees) {
        tokens = new address[](1);
        amounts = new uint256[](1);
        fees = new uint256[](1);
        tokens[0] = token;
        amounts[0] = amount;
        fees[0] = 0;
    }

    function test_balancer_rejects_wrong_token() public {
        (address[] memory tokens, uint256[] memory amounts, uint256[] memory fees) = _one(BAD, 1e6);
        vm.expectRevert();
        balancer.callCallback(executor, tokens, amounts, fees, _data(2, address(balancer), BORROW));
    }

    function test_balancer_rejects_wrong_amount() public {
        (address[] memory tokens, uint256[] memory amounts, uint256[] memory fees) = _one(BORROW, 2e6);
        vm.expectRevert();
        balancer.callCallback(executor, tokens, amounts, fees, _data(2, address(balancer), BORROW));
    }

    function test_balancer_rejects_wrong_shape() public {
        address[] memory tokens = new address[](2);
        uint256[] memory amounts = new uint256[](2);
        uint256[] memory fees = new uint256[](2);
        tokens[0] = BORROW;
        tokens[1] = MID;
        amounts[0] = 1e6;
        amounts[1] = 1;
        vm.expectRevert();
        balancer.callCallback(executor, tokens, amounts, fees, _data(2, address(balancer), BORROW));
    }

    function test_balancer_rejects_wrong_provider_type() public {
        (address[] memory tokens, uint256[] memory amounts, uint256[] memory fees) = _one(BORROW, 1e6);
        vm.expectRevert();
        balancer.callCallback(executor, tokens, amounts, fees, _data(0, address(balancer), BORROW));
    }

    function test_balancer_rejects_stale_execution_id() public {
        (address[] memory tokens, uint256[] memory amounts, uint256[] memory fees) = _one(BORROW, 1e6);
        bytes memory data = abi.encode(
            keccak256("stale"), uint8(2), address(balancer), BORROW, uint256(1e6), uint8(0), ROUTER_A,
            _path(BORROW, MID), uint256(1), uint8(0), ROUTER_B, _path(MID, BORROW), uint256(1),
            uint256(0), uint256(5_000_000), block.timestamp + 1_000, bytes("")
        );
        vm.expectRevert();
        balancer.callCallback(executor, tokens, amounts, fees, data);
    }

    function test_v3_rejects_wrong_borrow_asset() public {
        bytes memory data = _data(1, address(pool), BAD);
        vm.expectRevert();
        pool.callCallback(executor, 0, 0, data);
    }

    function test_v3_rejects_wrong_provider_binding() public {
        bytes memory data = _data(1, address(balancer), BORROW);
        vm.expectRevert();
        pool.callCallback(executor, 0, 0, data);
    }

    function test_v3_rejects_wrong_provider_type() public {
        bytes memory data = _data(0, address(pool), BORROW);
        vm.expectRevert();
        pool.callCallback(executor, 0, 0, data);
    }

    function test_v3_rejects_stale_execution_id() public {
        bytes memory data = abi.encode(
            keccak256("stale-v3"), uint8(1), address(pool), BORROW, uint256(1e6), uint8(0), ROUTER_A,
            _path(BORROW, MID), uint256(1), uint8(0), ROUTER_B, _path(MID, BORROW), uint256(1),
            uint256(0), uint256(5_000_000), block.timestamp + 1_000, bytes("")
        );
        vm.expectRevert();
        pool.callCallback(executor, 0, 0, data);
    }
}
