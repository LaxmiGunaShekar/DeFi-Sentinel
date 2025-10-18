// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SentimentOracle {
    mapping(uint256 => string) public sentimentHistory;

    /**
     * @notice Called by the AI agent to submit a new sentiment data hash.
     * @param _timestamp The current Unix timestamp.
     * @param _ipfsHash The IPFS CID of the sentiment analysis report.
     */
    function submitSentiment(
        uint256 _timestamp,
        string memory _ipfsHash
    ) public {
        sentimentHistory[_timestamp] = _ipfsHash;
    }

    /**
     * @notice Allows other smart contracts or users to retrieve the hash for a given timestamp.
     * @param _timestamp The timestamp to look up.
     * @return The IPFS CID string.
     */
    function getSentiment(
        uint256 _timestamp
    ) public view returns (string memory) {
        return sentimentHistory[_timestamp];
    }
}
