# DeFi Sentinel - The AI Agent (Backend)

This folder contains the "brain" of the DeFi Sentinel project. It's a Python agent responsible for fetching real-world data, analyzing it with an AI model, and sending transactions to the blockchain to update the oracle.

This agent is deployed as a serverless job using **GitHub Actions** (see `.github/workflows/main.yml` in the root).

## Core Functionality

The `agent.py` script is the heart of this component. When it runs, it performs the following sequence:

1.  **Load Secrets:** Loads all API keys and the private key from environment variables.
2.  **Fetch Tweets:** Connects to the X API using `tweepy` to find recent, high-signal tweets.
3.  **Analyze Sentiment:** Uses a pre-trained `transformers` model (`distilbert-base-uncased-finetuned-sst-2-english`) to score each tweet. A positive score is given for "POSITIVE" and a negative score for "NEGATIVE".
4.  **Calculate Average:** Computes the average sentiment score for the entire batch of tweets.
5.  **Upload to IPFS:** Packages the full results (tweets, individual scores, and average score) into a JSON file and uploads it to IPFS via the Pinata API.
6.  **Submit to Oracle:** Connects to the Polygon Amoy testnet via `web3.py` and calls the `submitSentiment` function on the `SentimentOracle` contract, passing in the new IPFS hash.
7.  **Manage Protocol State:** Checks the new `average_sentiment` score.
    * If `score < RISK_THRESHOLD` and the protocol is not paused, it sends a transaction to `triggerPause()`.
    * If `score >= RISK_THRESHOLD` and the protocol *is* paused, it sends a transaction to `unpause()`.

## Key Files
* `agent.py`: The main Python script that runs the entire ETL (Extract, Transform, Load) and transaction-sending process.
* `requirements.txt`: The list of all Python dependencies needed to run the agent (e.g., `tweepy`, `transformers`, `web3`).
* `abi.json` / `mock_abi.json`: The ABIs (Application Binary Interfaces) that tell `web3.py` how to format transactions for my smart contracts.
* `contracts/`: Contains the original Solidity source code for the smart contracts.

## How to Run Locally

While this is deployed on GitHub Actions, you can run it on your own machine.

1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/LaxmiGunaShekar/DeFi-Sentinel.git](https://github.com/LaxmiGunaShekar/DeFi-Sentinel.git)
    cd DeFi-Sentinel/DeFi-Sentinel
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create `.env` file:**
    Create a file named `.env` in this folder and fill it with your keys.
    ```
    TWITTER_BEARER_TOKEN=...
    PINATA_API_KEY=...
    PINATA_API_SECRET=...
    ALCHEMY_API_URL=...
    PRIVATE_KEY=...
    CONTRACT_ADDRESS=...
    MOCK_DEFI_ADDRESS=...
    ```
4.  **Run the Agent:**
    ```bash
    python agent.py
    ```