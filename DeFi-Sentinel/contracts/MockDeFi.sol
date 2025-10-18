// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Import the interface of our first contract so we can talk to it.
import "./SentimentOracle.sol";

/**
 * @title MockDeFi
 * @notice A simple contract that simulates a DeFi protocol.
 * It can be paused by checking the sentiment from our oracle.
 */
contract MockDeFi {
    // A variable to store a reference to our deployed SentimentOracle contract.
    SentimentOracle public oracle;

    // The "on/off" switch for our protocol. 'public' means anyone can read its value.
    bool public paused;

    /**
     * @notice When we deploy this contract, we must give it the address
     * of the already deployed SentimentOracle.
     * @param _oracleAddress The address of the SentimentOracle contract.
     */
    constructor(address _oracleAddress) {
        oracle = SentimentOracle(_oracleAddress);
    }

    /**
     * @notice This is a placeholder function. It reads the IPFS hash from the oracle.
     * @param _timestamp The timestamp to check the sentiment for.
     */
    function checkRisk(uint256 _timestamp) public view {
        // <-- FIXED: Added 'view' keyword
        // 1. Get the IPFS hash from our oracle contract.
        oracle.getSentiment(_timestamp); // <-- FIXED: Removed unused variable

        // 2. IMPORTANT: A smart contract cannot read from IPFS or process JSON.
        // In the full system, an off-chain script would read the IPFS hash,
        // get the actual sentiment score, and then call another function
        // here if the score is bad.

        // For our simulation, we will add a separate function to manually trigger the pause.
    }

    /**
     * @notice An external, trusted owner (or our Python agent in a later step)
     * would call this function to pause the contract in an emergency.
     */
    function triggerPause() public {
        // In a real contract, you would add security here to ensure only
        // a trusted address can call this. For our project, it's open.
        paused = true;
    }
}
