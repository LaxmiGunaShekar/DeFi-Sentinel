import os
import json
import time
import requests
import tweepy
from dotenv import load_dotenv
from transformers import pipeline
from web3 import Web3

# --- DEBUG MODE & RISK THRESHOLD ---
# Set to False to run with the corrected, high-quality query
DEBUG_MODE = False
RISK_THRESHOLD = -0.3 
# ------------------------------------

# Load environment variables
load_dotenv()
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
pinata_api_key = os.getenv("PINATA_API_KEY")
pinata_api_secret = os.getenv("PINATA_API_SECRET")
alchemy_api_url = os.getenv("ALCHEMY_API_URL")
private_key = os.getenv("PRIVATE_KEY")
oracle_contract_address = os.getenv("CONTRACT_ADDRESS")
mock_defi_address = os.getenv("MOCK_DEFI_ADDRESS")

# --- Blockchain Setup ---
w3 = Web3(Web3.HTTPProvider(alchemy_api_url))

# Load Oracle Contract ABI
try:
    with open('abi.json', 'r') as f:
        oracle_abi = json.load(f)
    oracle_contract = w3.eth.contract(address=oracle_contract_address, abi=oracle_abi)
except Exception as e:
    print(f"Error loading Oracle ABI or Contract: {e}")
    exit()

# Load Mock DeFi Contract ABI
try:
    with open('mock_abi.json', 'r') as f:
        mock_abi = json.load(f)
    mock_defi_contract = w3.eth.contract(address=mock_defi_address, abi=mock_abi)
except Exception as e:
    print(f"Error loading Mock DeFi ABI or Contract: {e}")
    exit()

# Get account from private key
try:
    my_account = w3.eth.account.from_key(private_key)
    print(f"Agent Wallet Address: {my_account.address}")
except Exception as e:
    print(f"Error loading private key: {e}")
    exit()
# -------------------------

# Initialize AI Model
print("Loading sentiment analysis model...")
sentiment_classifier = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
print("Model loaded successfully!")


def upload_to_pinata(json_data):
    """Uploads JSON to Pinata and returns the IPFS hash."""
    print("\nUploading results to IPFS via Pinata...")
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {"Content-Type": "application/json", "pinata_api_key": pinata_api_key, "pinata_secret_api_key": pinata_api_secret}
    try:
        response = requests.post(url, json=json_data, headers=headers)
        response.raise_for_status()
        ipfs_hash = response.json()["IpfsHash"]
        print(f"IPFS Hash (CID): {ipfs_hash}")
        return ipfs_hash
    except requests.exceptions.RequestException as e:
        print(f"An IPFS error occurred: {e}")
        return None

def submit_hash_to_blockchain(ipfs_hash):
    """Submits the IPFS hash to the SentimentOracle contract."""
    print("\nPreparing to submit hash to the Oracle contract...")
    try:
        timestamp = int(time.time())
        # Ensure nonce is always fresh before sending a transaction
        nonce = w3.eth.get_transaction_count(my_account.address)
        tx = oracle_contract.functions.submitSentiment(timestamp, ipfs_hash).build_transaction({
            'from': my_account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("Oracle transaction sent! Waiting for confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120) # Added timeout
        print(f"Oracle submission successful! Tx: {w3.to_hex(tx_hash)}")
        return True
    except Exception as e:
        print(f"A blockchain error occurred during oracle submission: {e}")
        return False


# --- UPGRADED: Pause/Unpause Logic ---
def manage_defi_contract_state(sentiment_score):
    """Checks sentiment and pauses or unpauses the MockDeFi contract."""
    try:
        current_pause_state = mock_defi_contract.functions.paused().call()
        print(f"Current MockDeFi Paused State: {current_pause_state}")

        nonce = w3.eth.get_transaction_count(my_account.address) # Get nonce before potential transaction

        if sentiment_score < RISK_THRESHOLD and not current_pause_state:
            print(f"\nSentiment score ({sentiment_score:.4f}) is below threshold. Pausing contract...")
            tx = mock_defi_contract.functions.triggerPause().build_transaction({
                'from': my_account.address, 'nonce': nonce, 'gas': 100000, 'gasPrice': w3.eth.gas_price
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Pause transaction sent! Waiting for confirmation...")
            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print(f"--- PAUSE SUCCESS --- Tx: {w3.to_hex(tx_hash)}")

        elif sentiment_score >= RISK_THRESHOLD and current_pause_state:
            print(f"\nSentiment score ({sentiment_score:.4f}) is above threshold. Unpausing contract...")
            tx = mock_defi_contract.functions.unpause().build_transaction({
                'from': my_account.address, 'nonce': nonce, 'gas': 100000, 'gasPrice': w3.eth.gas_price
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("Unpause transaction sent! Waiting for confirmation...")
            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print(f"--- UNPAUSE SUCCESS --- Tx: {w3.to_hex(tx_hash)}")

        else:
            print(f"\nSentiment score ({sentiment_score:.4f}) is within acceptable range or contract is already in the correct state. No action needed.")

    except Exception as e:
        print(f"An error occurred while managing contract state: {e}")
# --------------------------------------

def run_agent():
    """Main function to run the full agent logic."""
    print("\n--- DeFi Sentinel Agent Initializing ---")
    tweet_texts = []

    if DEBUG_MODE:
        print("--- Running in DEBUG MODE: Using local data from test_data.json ---")
        try:
            with open('test_data.json', 'r', encoding='utf-8') as f: # Added encoding
                tweet_texts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: test_data.json not found or corrupted. Cannot run in debug mode.")
            return
    else:
        print("--- Running in LIVE MODE ---")
        try:
            client = tweepy.Client(bearer_token)
            # Fetching 10 high-signal tweets
            query = "(from:VitalikButerin OR from:aantop OR from:haydenzadams OR from:StaniKulechov) (DeFi OR Ethereum OR ETH) -is:retweet -is:reply lang:en"
            print("Fetching recent tweets from influential accounts for query:", query)
            response = client.search_recent_tweets(query=query, max_results=10)

            if response.data:
                tweet_texts = [tweet.text for tweet in response.data]
                with open('test_data.json', 'w', encoding='utf-8') as f:
                    json.dump(tweet_texts, f, indent=2)
                print(f"Successfully fetched and saved {len(tweet_texts)} high-signal tweets.")
            else:
                print("No recent tweets found from the specified influential accounts.")
                # We can still proceed with sentiment analysis if needed, using old data or default
                # Or simply return if no new data means no action
                return 
        except Exception as e:
            print(f"An API error occurred: {e}")
            return

    if not tweet_texts:
        print("Cannot calculate sentiment, no tweets to process.")
        return

    print(f"\nAnalyzing sentiment of {len(tweet_texts)} tweets...")
    sentiment_scores = sentiment_classifier(tweet_texts)
    total_score = 0
    detailed_results = []
    for tweet, sentiment in zip(tweet_texts, sentiment_scores):
        numeric_score = sentiment['score'] if sentiment['label'] == 'POSITIVE' else -sentiment['score']
        total_score += numeric_score
        detailed_results.append({'text': tweet, 'label': sentiment['label'], 'score': sentiment['score']})

    average_sentiment = total_score / len(tweet_texts)
    print(f"Average Sentiment Score: {average_sentiment:.4f}")

    results_json = { "average_sentiment": average_sentiment, "detailed_results": detailed_results }
    ipfs_cid = upload_to_pinata(results_json)

    if ipfs_cid:
        if submit_hash_to_blockchain(ipfs_cid):
            # Only manage state if the oracle submission was successful
            manage_defi_contract_state(average_sentiment)


if __name__ == "__main__":
    run_agent()