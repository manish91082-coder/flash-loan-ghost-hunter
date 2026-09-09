// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IERC20 { function balanceOf(address account) external view returns (uint256); function transfer(address recipient, uint256 amount) external returns (bool); function approve(address spender, uint256 amount) external returns (bool); }

library SafeERC20 {
    function safeTransfer(IERC20 token, address to, uint256 value) internal { (bool success, bytes memory data) = address(token).call(abi.encodeWithSelector(IERC20.transfer.selector, to, value)); require(success && (data.length == 0 || abi.decode(data, (bool))), "SafeERC20: transfer failed"); }
    function safeApprove(IERC20 token, address spender, uint256 value) internal {
        (bool success, bytes memory data) = address(token).call(abi.encodeWithSelector(IERC20.approve.selector, spender, value));
        if(!success || (data.length > 0 && !abi.decode(data, (bool)))) {
            (bool success0, bytes memory data0) = address(token).call(abi.encodeWithSelector(IERC20.approve.selector, spender, 0)); require(success0 && (data0.length == 0 || abi.decode(data0, (bool))), "SafeERC20: approve 0 failed");
            (bool success1, bytes memory data1) = address(token).call(abi.encodeWithSelector(IERC20.approve.selector, spender, value)); require(success1 && (data1.length == 0 || abi.decode(data1, (bool))), "SafeERC20: approve failed");
        }
    }
}

interface IPool { function flashLoanSimple(address receiverAddress, address asset, uint256 amount, bytes calldata params, uint16 referralCode) external; }
interface IUniswapV3Pool { function token0() external view returns (address); function token1() external view returns (address); function flash(address recipient, uint256 amount0, uint256 amount1, bytes calldata data) external; }
interface IBalancerVault { function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external; }
interface IUniswapV2Router { function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) external returns (uint[] memory amounts); }
interface ISwapRouter {
    struct ExactInputSingleParams { address tokenIn; address tokenOut; uint24 fee; address recipient; uint256 deadline; uint256 amountIn; uint256 amountOutMinimum; uint160 sqrtPriceLimitX96; }
    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
    struct ExactInputParams { bytes path; address recipient; uint256 deadline; uint256 amountIn; uint256 amountOutMinimum; }
    function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
}

contract PhantomX_Production_Executor {
    address public owner;
    mapping(address => bool) public isAavePool;
    mapping(address => bool) public isBalancerVault;
    mapping(address => bool) public isUniswapV3Pool;
    mapping(address => bool) public allowedRouters;
    mapping(address => bool) public allowedTokens;
    using SafeERC20 for IERC20;
    mapping(bytes32 => bool) public usedIntents;
    bool private _locked;
    bool public paused;

    enum FlashProviderType { AAVE, UNISWAP_V3, BALANCER }
    enum SwapType { V2, V3 }

    bytes32 private constant EIP712_DOMAIN_TYPEHASH = keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)");
    bytes32 private constant EXECUTION_INTENT_TYPEHASH = keccak256("ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)");
    bytes32 public DOMAIN_SEPARATOR;
    bytes32 public activeExecutionId;

    struct ExecutionIntent {
        bytes32 executionId; FlashProviderType providerType; address providerAddress; address tokenBorrow; uint256 amountBorrow; SwapType swap1Type; address routerA; bytes pathA; uint256 minAmountOut1; SwapType swap2Type; address routerB; bytes pathB; uint256 minAmountOutFinal; uint256 minimumOnChainSurplus; uint256 maximumGasLimit; uint256 deadline; bytes signature;
    }

    modifier nonReentrant() { require(!_locked, "ReentrancyGuard"); _locked = true; _; _locked = false; }
    modifier onlyOwner() { require(msg.sender == owner, "Not owner"); _; }
    modifier notPaused() { require(!paused, "Contract paused"); _; }

    constructor() { owner = msg.sender; DOMAIN_SEPARATOR = keccak256(abi.encode(EIP712_DOMAIN_TYPEHASH, keccak256(bytes("PhantomX Executor")), keccak256(bytes("1")), block.chainid, address(this))); }

    function transferOwnership(address newOwner) external onlyOwner { require(newOwner != address(0), "Zero address"); owner = newOwner; }
    function setPaused(bool _paused) external onlyOwner { paused = _paused; }
    function setAavePool(address _pool, bool _status) external onlyOwner { isAavePool[_pool] = _status; }
    function setBalancerVault(address _vault, bool _status) external onlyOwner { isBalancerVault[_vault] = _status; }
    function setUniswapV3Pool(address _pool, bool _status) external onlyOwner { isUniswapV3Pool[_pool] = _status; }
    function setRouter(address _router, bool _status) external onlyOwner { allowedRouters[_router] = _status; }
    function setToken(address _token, bool _status) external onlyOwner { allowedTokens[_token] = _status; }

    function _verifyIntentSignature(ExecutionIntent memory intent) internal view returns (bool) {
        bytes32 structHash = keccak256(abi.encode(
            EXECUTION_INTENT_TYPEHASH,
            intent.executionId,
            intent.providerType,
            intent.providerAddress,
            intent.tokenBorrow,
            intent.amountBorrow,
            intent.swap1Type,
            intent.routerA,
            keccak256(intent.pathA),
            intent.minAmountOut1,
            intent.swap2Type,
            intent.routerB,
            keccak256(intent.pathB),
            intent.minAmountOutFinal,
            intent.minimumOnChainSurplus,
            intent.maximumGasLimit,
            intent.deadline
        ));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
        require(intent.signature.length == 65, "Invalid sig length");
        bytes32 r; bytes32 s; uint8 v; bytes memory sig = intent.signature;
        assembly { r := mload(add(sig, 32)) s := mload(add(sig, 64)) v := byte(0, mload(add(sig, 96))) }
        return ecrecover(digest, v, r, s) == owner;
    }

    function executeOpportunity(ExecutionIntent memory intent) external notPaused nonReentrant {
        uint256 gasStart = gasleft();
        require(_verifyIntentSignature(intent), "Invalid Intent Signature"); require(block.timestamp <= intent.deadline, "Expired"); require(!usedIntents[intent.executionId], "Intent replayed"); require(intent.amountBorrow > 0, "Zero borrow amount"); require(intent.maximumGasLimit > 0, "Zero gas limit"); require(intent.minAmountOut1 > 0 && intent.minAmountOutFinal > 0, "Zero minimum output");
        usedIntents[intent.executionId] = true; bytes memory params = abi.encode(intent); activeExecutionId = intent.executionId;
        if (intent.providerType == FlashProviderType.AAVE) { require(isAavePool[intent.providerAddress], "Invalid Aave Pool"); IPool(intent.providerAddress).flashLoanSimple(address(this), intent.tokenBorrow, intent.amountBorrow, params, 0); }
        else if (intent.providerType == FlashProviderType.UNISWAP_V3) { require(isUniswapV3Pool[intent.providerAddress], "Invalid UniV3 Pool"); address token0 = IUniswapV3Pool(intent.providerAddress).token0(); address token1 = IUniswapV3Pool(intent.providerAddress).token1(); uint256 amount0 = intent.tokenBorrow == token0 ? intent.amountBorrow : 0; uint256 amount1 = intent.tokenBorrow == token1 ? intent.amountBorrow : 0; require(amount0 > 0 || amount1 > 0, "Borrow token not in pool"); IUniswapV3Pool(intent.providerAddress).flash(address(this), amount0, amount1, params); }
        else if (intent.providerType == FlashProviderType.BALANCER) { require(isBalancerVault[intent.providerAddress], "Invalid Balancer Vault"); address[] memory tokens = new address[](1); tokens[0] = intent.tokenBorrow; uint256[] memory amounts = new uint256[](1); amounts[0] = intent.amountBorrow; IBalancerVault(intent.providerAddress).flashLoan(address(this), tokens, amounts, params); }
        else { revert("Unknown Provider"); }
        activeExecutionId = bytes32(0); require(gasStart - gasleft() <= intent.maximumGasLimit, "Gas limit exceeded");
    }

    function _validateV2Path(bytes memory path, address borrowToken, bool finalLeg) internal pure returns (address[] memory decodedPath) {
        decodedPath = abi.decode(path, (address[])); require(decodedPath.length >= 2, "V2 path too short"); require(decodedPath[0] != address(0), "V2 path starts zero");
        if (!finalLeg) require(decodedPath[0] == borrowToken, "V2 leg1 input mismatch"); if (finalLeg) require(decodedPath[decodedPath.length - 1] == borrowToken, "V2 final token mismatch");
    }

    function _validateV3Path(bytes memory path, address borrowToken, bool finalLeg) internal pure {
        require(path.length >= 43 && (path.length - 20) % 23 == 0, "V3 path malformed"); address first; address last;
        assembly { first := shr(96, mload(add(path, 32))) last := shr(96, mload(add(path, add(32, sub(mload(path), 20))))) }
        if (!finalLeg) require(first == borrowToken, "V3 leg1 input mismatch"); if (finalLeg) require(last == borrowToken, "V3 final token mismatch");
    }

    function _firstToken(SwapType swapType, bytes memory path) internal pure returns (address token) {
        if (swapType == SwapType.V2) { address[] memory p = abi.decode(path, (address[])); require(p.length >= 2, "V2 path too short"); return p[0]; }
        if (swapType == SwapType.V3) { require(path.length >= 43 && (path.length - 20) % 23 == 0, "V3 path malformed"); bytes32 w; assembly { w := mload(add(path, 32)) } return address(bytes20(w)); }
        revert("Invalid SwapType");
    }

    function _lastToken(SwapType swapType, bytes memory path) internal pure returns (address token) {
        if (swapType == SwapType.V2) { address[] memory p = abi.decode(path, (address[])); require(p.length >= 2, "V2 path too short"); return p[p.length - 1]; }
        if (swapType == SwapType.V3) { require(path.length >= 43 && (path.length - 20) % 23 == 0, "V3 path malformed"); bytes32 w; uint256 n; assembly { n := mload(path) w := mload(add(path, add(32, sub(n, 20)))) } return address(bytes20(w)); }
        revert("Invalid SwapType");
    }

    function _executeRoute(ExecutionIntent memory intent) internal returns (uint256 finalAmount) {
        require(allowedRouters[intent.routerA] && allowedRouters[intent.routerB], "Unauthorized router"); require(allowedTokens[intent.tokenBorrow], "Unauthorized borrow token");
        if (intent.swap1Type == SwapType.V2) { _validateV2Path(intent.pathA, intent.tokenBorrow, false); } else { _validateV3Path(intent.pathA, intent.tokenBorrow, false); }
        if (intent.swap2Type == SwapType.V2) { _validateV2Path(intent.pathB, intent.tokenBorrow, true); } else { _validateV3Path(intent.pathB, intent.tokenBorrow, true); }
        require(_lastToken(intent.swap1Type, intent.pathA) == _firstToken(intent.swap2Type, intent.pathB), "Route token discontinuity");
        uint256 out1 = _swap(intent.swap1Type, intent.routerA, intent.pathA, intent.amountBorrow, intent.minAmountOut1, intent.deadline); finalAmount = _swap(intent.swap2Type, intent.routerB, intent.pathB, out1, intent.minAmountOutFinal, intent.deadline); return finalAmount;
    }

    function _swap(SwapType swapType, address router, bytes memory path, uint256 amountIn, uint256 minAmountOut, uint256 deadline) internal returns (uint256) {
        address tokenIn = _firstToken(swapType, path); IERC20(tokenIn).safeApprove(router, amountIn);
        if (swapType == SwapType.V2) { address[] memory decodedPath = abi.decode(path, (address[])); uint[] memory amounts = IUniswapV2Router(router).swapExactTokensForTokens(amountIn, minAmountOut, decodedPath, address(this), deadline); return amounts[amounts.length - 1]; }
        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({path: path, recipient: address(this), deadline: deadline, amountIn: amountIn, amountOutMinimum: minAmountOut}); return ISwapRouter(router).exactInput(params);
    }

    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns (bool) {
        require(msg.sender == _activeAaveProvider(params), "Untrusted callback"); require(initiator == address(this), "Untrusted initiator"); require(activeExecutionId != bytes32(0), "No active execution"); ExecutionIntent memory intent = abi.decode(params, (ExecutionIntent)); require(intent.providerType == FlashProviderType.AAVE, "Wrong provider type"); require(msg.sender == intent.providerAddress && isAavePool[msg.sender], "Untrusted Aave provider"); require(intent.executionId == activeExecutionId, "Active ID mismatch"); require(asset == intent.tokenBorrow && amount == intent.amountBorrow, "Asset/amount mismatch");
        uint256 balanceBefore = IERC20(asset).balanceOf(address(this)); uint256 finalAmount = _executeRoute(intent); uint256 totalRepayment = amount + premium; require(finalAmount >= totalRepayment + intent.minimumOnChainSurplus, "MinProfit failed"); require(IERC20(asset).balanceOf(address(this)) >= balanceBefore - amount + totalRepayment, "Insufficient balance"); IERC20(asset).safeApprove(msg.sender, totalRepayment); return true;
    }
    function _activeAaveProvider(bytes calldata params) internal pure returns (address) { ExecutionIntent memory intent = abi.decode(params, (ExecutionIntent)); return intent.providerAddress; }

    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory userData) external {
        require(activeExecutionId != bytes32(0), "No active execution"); ExecutionIntent memory intent = abi.decode(userData, (ExecutionIntent)); require(intent.providerType == FlashProviderType.BALANCER, "Wrong provider type"); require(msg.sender == intent.providerAddress && isBalancerVault[msg.sender], "Untrusted Balancer provider"); require(intent.executionId == activeExecutionId, "Active ID mismatch"); require(tokens.length == 1 && amounts.length == 1 && feeAmounts.length == 1, "Flash loan shape mismatch"); require(tokens[0] == intent.tokenBorrow && amounts[0] == intent.amountBorrow, "Asset/amount mismatch");
        uint256 balanceBefore = IERC20(tokens[0]).balanceOf(address(this)); uint256 finalAmount = _executeRoute(intent); uint256 totalRepayment = amounts[0] + feeAmounts[0]; require(finalAmount >= totalRepayment + intent.minimumOnChainSurplus, "MinProfit failed"); require(IERC20(tokens[0]).balanceOf(address(this)) >= balanceBefore - amounts[0] + totalRepayment, "Insufficient balance"); IERC20(tokens[0]).safeTransfer(msg.sender, totalRepayment);
    }

    function uniswapV3FlashCallback(uint256 fee0, uint256 fee1, bytes calldata data) external {
        require(activeExecutionId != bytes32(0), "No active execution"); ExecutionIntent memory intent = abi.decode(data, (ExecutionIntent)); require(intent.providerType == FlashProviderType.UNISWAP_V3, "Wrong provider type"); require(msg.sender == intent.providerAddress && isUniswapV3Pool[msg.sender], "Untrusted UniV3 provider"); require(intent.executionId == activeExecutionId, "Active ID mismatch"); address token0 = IUniswapV3Pool(msg.sender).token0(); address token1 = IUniswapV3Pool(msg.sender).token1(); require(intent.tokenBorrow == token0 || intent.tokenBorrow == token1, "Asset mismatch"); uint256 fee = intent.tokenBorrow == token0 ? fee0 : fee1; uint256 totalRepayment = intent.amountBorrow + fee;
        uint256 balanceBefore = IERC20(intent.tokenBorrow).balanceOf(address(this)); uint256 finalAmount = _executeRoute(intent); require(finalAmount >= totalRepayment + intent.minimumOnChainSurplus, "MinProfit failed"); require(IERC20(intent.tokenBorrow).balanceOf(address(this)) >= balanceBefore - intent.amountBorrow + totalRepayment, "Insufficient balance"); IERC20(intent.tokenBorrow).safeTransfer(msg.sender, totalRepayment);
    }

    function withdraw(address token) external onlyOwner { uint256 balance = IERC20(token).balanceOf(address(this)); IERC20(token).safeTransfer(owner, balance); }
    function withdrawNative() external onlyOwner { payable(owner).transfer(address(this).balance); }
    receive() external payable {}
}
