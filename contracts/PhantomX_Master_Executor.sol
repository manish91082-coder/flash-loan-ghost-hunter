// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

/**
 * @title PhantomX_Master_Executor
 * @dev Modular Architecture for Extreme Saturation Master Goal.
 * Supports: Arbitrage, Liquidations, Collateral Swapping.
 */

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IFlashLoanProvider {
    function flashLoan(address receiver, address token, uint256 amount, bytes calldata data) external;
}

// ---------------------- MODULE INTERFACES ----------------------

interface IStrategyModule {
    function executeStrategy(address token, uint256 amount, bytes calldata data) external returns (uint256 finalBalance);
}

// ---------------------------------------------------------------

contract PhantomX_Master_Executor {
    address public immutable ownerWallet;
    
    // Whitelisted strategy modules (e.g. AaveLiquidator, DEXArbitrage)
    mapping(address => bool) public approvedModules;
    
    constructor(address _coldWallet) {
        ownerWallet = _coldWallet;
    }

    function addModule(address module) external {
        require(msg.sender == ownerWallet, "Only owner");
        approvedModules[module] = true;
    }

    // @dev Triggered by the Serverless Opportunity Engine.
    function executeStrategyFlash(
        address flashProvider,
        address token,
        uint256 flashAmount,
        address strategyModule,
        bytes calldata strategyData
    ) external {
        require(approvedModules[strategyModule], "Unauthorized strategy module");
        
        // Encode the target module into the payload for the callback
        bytes memory payload = abi.encode(strategyModule, strategyData);
        
        IFlashLoanProvider(flashProvider).flashLoan(address(this), token, flashAmount, payload);
    }

    // @dev The universal callback from the Flash Loan Provider
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        address initiator,
        bytes calldata payload
    ) external returns (bool) {
        
        // 1. Decode module and data
        (address strategyModule, bytes memory strategyData) = abi.decode(payload, (address, bytes));
        
        // 2. Transfer flash funds to the specific module and execute
        IERC20(token).transfer(strategyModule, amount);
        uint256 finalBalanceReturned = IStrategyModule(strategyModule).executeStrategy(token, amount, strategyData);
        
        // 3. Mathematical Veto
        uint256 amountToRepay = amount + fee;
        require(finalBalanceReturned >= amountToRepay, "PhantomX Veto: Strategy resulted in a loss. Reverting.");
        
        // 4. Repay Flash Loan
        IERC20(token).approve(msg.sender, amountToRepay);
        
        // 5. Transfer Delta (Profit)
        uint256 profit = finalBalanceReturned - amountToRepay;
        if (profit > 0) {
            IERC20(token).transfer(ownerWallet, profit);
        }
        
        return true;
    }
}
