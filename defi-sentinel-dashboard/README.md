# DeFi Sentinel - The Dashboard (Frontend)

This folder contains the React (Vite) frontend for the DeFi Sentinel project. It's the "window" into the system, allowing any user to view the on-chain status of the oracle and the mock protocol.

This dashboard is deployed live on **Vercel**.

## Features

* **Live Protocol Status:** Connects to the `MockDeFi` contract and reads its `paused` state, displaying either "OPERATIONAL" (in green) or "SYSTEM PAUSED" (in red).
* **Live Sentiment Score:** Connects to the `SentimentOracle` contract, finds the latest IPFS hash, and fetches the JSON data from IPFS. It then displays the `average_sentiment` score.
* **Dynamic Colors:** The score's color changes based on its value (green for positive, red for negative, yellow for neutral).
* **Animated Tweet Ticker:** The "Live Market Sentiment" box streams the actual tweets that were analyzed in the most recent run,
* **Responsive Design:** Built to be viewable on both desktop and mobile.

## Key Files
* `src/App.jsx`: The main React component. It contains all logic for:
    * Connecting to the blockchain with `ethers.js`.
    * Fetching data from both smart contracts.
    * Fetching the JSON data from the `ipfs.io` gateway.
    * Managing all application state (e.g., `isLoading`, `isPaused`, `sentimentScore`).
* `src/App.css`: Contains all the styling, including the glassmorphism effects, animations, and color scheme.
* `src/abi.json` / `src/mock_abi.json`: The ABIs needed by `ethers.js` to understand how to read data from my smart contracts.
* `main.jsx`: The entry point for the React application.

## How to Run Locally

1.  **Navigate to this folder:**
    ```bash
    # From the root of the project
    cd defi-sentinel-dashboard
    ```
2.  **Install Dependencies:**
    ```bash
    npm install
    ```
3.  **Run the Development Server:**
    ```bash
    npm run dev
    ```
    This will open the dashboard on `http://localhost:5173` (or a similar port).