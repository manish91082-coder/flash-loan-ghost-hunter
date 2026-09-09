# 6. Smart Contracts and On-Chain Logic

## 6.1 Master Solidity Contract (`UniversalFlashExecutor.sol`)
A unified smart contract designed to request flash loans and execute trades in a single atomic transaction.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IUniswapV2Router {
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

// Minimal Aave V3 Flash Loan Receiver Interface
interface IPool {
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

contract UniversalFlashExecutor {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // Fallback to receive ETH
    receive() external payable {}
    
    // Core Arbitrage Logic (can be called by Aave callback, or directly for testing)
    function executeSpatialArbitrage(
        address tokenBorrow,
        uint256 amountIn,
        address routerA,
        address routerB,
        address tokenPath
    ) public returns (uint256 profit) {
        
        // 1. Swap on Router A
        IERC20(tokenBorrow).approve(routerA, amountIn);
        address[] memory pathA = new address[](2);
        pathA[0] = tokenBorrow;
        pathA[1] = tokenPath;
        
        uint[] memory amountsA = IUniswapV2Router(routerA).swapExactTokensForTokens(
            amountIn,
            0, // min amount (slippage handled by atomic revert if no profit)
            pathA,
            address(this),
            block.timestamp
        );
        
        uint256 intermediateTokenAmount = amountsA[1];
        
        // 2. Swap on Router B
        IERC20(tokenPath).approve(routerB, intermediateTokenAmount);
        address[] memory pathB = new address[](2);
        pathB[0] = tokenPath;
        pathB[1] = tokenBorrow;
        
        uint[] memory amountsB = IUniswapV2Router(routerB).swapExactTokensForTokens(
            intermediateTokenAmount,
            0,
            pathB,
            address(this),
            block.timestamp
        );
        
        uint256 amountOut = amountsB[1];
        
        // 3. Profit Check
        require(amountOut > amountIn, "Arbitrage not profitable");
        
        profit = amountOut - amountIn;
        return profit;
    }

    // Aave Flash Loan Callback
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        // Decode params
        (address routerA, address routerB, address tokenPath) = abi.decode(params, (address, address, address));
        
        // Execute Arbitrage
        uint256 profit = executeSpatialArbitrage(asset, amount, routerA, routerB, tokenPath);
        
        // Repay Flash Loan
        uint256 totalRepayment = amount + premium;
        require(IERC20(asset).balanceOf(address(this)) >= totalRepayment, "Insufficient funds to repay flash loan");
        
        IERC20(asset).approve(msg.sender, totalRepayment);
        return true;
    }
    
    function withdraw(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, balance);
    }
}

```
