# DeFi Sentinel: An AI-Powered Oracle for DeFi Protocol Protection 🛡️

**Welcome to our project!** This is DeFi Sentinel, a complete, end-to-end system we built to shield DeFi protocols from the extreme volatility caused by social media hype and "FUD" (Fear, Uncertainty, and Doubt).

It's not just a dashboard; it's a functioning, automated risk-management oracle.

---

## 🚀 Live Demo

**You can see the live dashboard here:** [**https://de-fi-sentinel-tan.vercel.app**](https://de-fi-sentinel-tan.vercel.app)

*(Note: The backend agent runs on a 6-hour schedule. The sentiment score you see is the most recent analysis from the last run.)*

---

## 1. The "Why": Our Project Vision

We've been fascinated by the world of **Decentralized Finance (DeFi)**. It has the power to create a more open and fair financial system, offering services like lending, borrowing, and trading without a traditional bank.

But this new frontier has a critical vulnerability.

### The Double-Edged Sword: DeFi & Social Media

DeFi markets are "permissionless," which also means they are incredibly susceptible to market sentiment. A single tweet from an influential figure, a wave of negative "FUD," or a coordinated hype campaign can send asset prices crashing or soaring in minutes.

**This creates a massive problem:**
* **For Users:** Their funds are at risk of sudden, sentiment-driven liquidation.
* **For Protocols:** A rapid "bank run" or price crash can drain liquidity pools, making the protocol insolvent.

Most protocols today are not equipped to react to this. Their risk parameters are static. They can't "see" the storm gathering on social media.

### Our Problem Statement

How can a DeFi protocol **autonomously protect itself** in real-time? How can it detect a significant, negative shift in market sentiment *before* it triggers a catastrophic cascade, and then *automatically* take defensive action?

---

## 2. The "What": Our Solution

Me and my team built **DeFi Sentinel** to be the answer.

It's an automated oracle system that we designed to **"watch, analyze, and act."**

* **Watch:** It constantly monitors social media (specifically X) for chatter from key, influential accounts in the DeFi space.
* **Analyze:** It uses an AI-powered sentiment analysis model to read these tweets and calculate a "Market Sentiment Score." A high score is positive (hype), and a low score is negative (FUD).
* **Act:** It submits this score to the blockchain. If the score drops below a pre-defined danger threshold, it automatically calls a function on a mock DeFi protocol, pausing its core functions to protect it from a "bank run." When the sentiment recovers, it automatically unpauses the protocol.

Our goal was to create a "circuit breaker" for DeFi, powered by real-world data.

### Core Features
* **🧠 AI-Powered Sentiment Agent:** A Python agent that fetches tweets, scores them with a `transformers` model, and uploads the results to IPFS.
* **⛓️ On-Chain Oracle Contract:** A custom `SentimentOracle.sol` contract that stores the IPFS hash of the sentiment report, creating an immutable, on-chain record.
* **🛡️ Mock DeFi Protocol:** A `MockDeFi.sol` contract with `pause()` and `unpause()` functions that can be *only* be triggered by my agent.
* **🌐 Real-time Dashboard:** A React frontend that reads data *directly* from the blockchain and IPFS, visualizing the current sentiment score, the protocol's status ("Operational" or "Paused"), and a live ticker of the tweets being analyzed.
* **🤖 Fully Automated:** The entire backend process is deployed using GitHub Actions, making it a "set it and forget it" serverless oracle.

---

## 3. The "How": System Architecture & Tech

We designed this project in three main components:

![A simple diagram showing Agent -> Contracts -> Dashboard](https://i.imgur.com/g0P4oYq.png)

### 1. The Backend (`DeFi-Sentinel` Folder)
This is the "brain" of the operation. It's a Python script that is deployed as a serverless function using **GitHub Actions**. Every 6 hours, it:
1.  Connects to the **X API**.
2.  Fetches tweets based on a query for influential accounts.
3.  Analyzes sentiment using the `transformers` library.
4.  Uploads the JSON report to **IPFS** via Pinata.
5.  Uses **Web3.py** to call `submitSentiment()` on my Oracle contract.
6.  Checks the score and calls `triggerPause()` or `unpause()` on my DeFi contract.

### 2. The Smart Contracts (`contracts` Folder)
* `SentimentOracle.sol`: The "record keeper." Its only job is to receive the IPFS hash from the agent and store it on-chain with a timestamp.
* `MockDeFi.sol`: The protocol I'm protecting. It has a `paused` variable and functions that my agent can call to protect the contract during high volatility.

### 3. The Frontend (`defi-sentinel-dashboard` Folder)
This is the "window" into the system. It's a **React (Vite)** application deployed on **Vercel**. It:
1.  Uses **ethers.js** to connect to the Polygon Amoy testnet.
2.  Reads the `paused()` state from the `MockDeFi` contract.
3.  Reads the `latestTimestamp` and `getSentiment` (IPFS hash) from the `SentimentOracle` contract.
4.  Fetches the JSON file from the IPFS gateway.
5.  Displays all this data in a clean, animated UI using **Framer Motion**.

---

## Project Structure

This repository is a "monorepo" containing both of the project's sub-folders.

* `/DeFi-Sentinel/`: The Python AI agent (backend).
* `/defi-sentinel-dashboard/`: The React dashboard (frontend).

Each folder contains its own detailed `README.md` with setup instructions and a description of its internal files.

## Future Goals

This project is a prototype, but it lays the foundation for a much more powerful system.
* **Expand Data Sources:** Integrate Reddit, news headlines, and other sources.
* **Improve AI Model:** Fine-tune a custom model on a crypto-specific dataset for better nuance (e.g., understanding "bullish" vs. "bearish").
* **Decentralize the Agent:** Run the Python agent on a decentralized oracle network like Chainlink to make the entire process trustless.

---

Thank you for checking out my project!