import { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { motion, AnimatePresence } from 'framer-motion';
import { FaBitcoin, FaDollarSign, FaUniversity } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6';
import './App.css';

// --- ACTION REQUIRED: PASTE YOUR FINAL, NEW INFO HERE ---
const ALCHEMY_API_URL = "https://polygon-amoy.g.alchemy.com/v2/WGD_BHKFgAQ8QS0YV-YFa";
const MOCK_DEFI_ADDRESS = "0x8Bccc445D3853eD5C6C7995463a0efA9225a0f91";
const SENTIMENT_ORACLE_ADDRESS = "0x81298d0A12addC1D3E873169284F54C6dbA1F460";
// -----------------------------------------------------------

// --- Tweet Ticker Component ---
const TweetTicker = ({ tweets }) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!tweets || tweets.length === 0) return;
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % tweets.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [tweets]);

  if (!tweets || tweets.length === 0) {
    return (
      <motion.div className="tweet-ticker" initial={{ y: -100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.8, delay: 0.5 }}>
        <div className="tweet-header">
            <FaXTwitter className="twitter-logo" />
            <span>Live Market Sentiment</span>
        </div>
         <div className="tweet-content"><p>Loading live tweets...</p></div>
      </motion.div>
    );
  }
  
  const currentTweet = tweets[index];

  return (
    <motion.div 
      className="tweet-ticker"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.5 }}
    >
      <div className="tweet-header">
        <FaXTwitter className="twitter-logo" />
        <span>Live Market Sentiment</span>
      </div>
      <div className="tweet-content">
        <AnimatePresence mode="wait">
          <motion.p
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.5 }}
          >
            {currentTweet.text}
          </motion.p>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

// --- CoinFlow Component ---
const CoinFlow = ({ CoinIcon, color, xStart, xEnd }) => {
  const coins = Array.from({ length: 5 });
  const duration = 5;
  return (
    <>
      {coins.map((_, i) => (
        <motion.div
          key={i} className="coin"
          style={{ color, filter: `drop-shadow(0 0 8px ${color})` }}
          initial={{ x: xStart, y: Math.random() * 40 - 20, opacity: 0 }}
          animate={{ x: [xStart, xEnd], opacity: [0, 1, 1, 0] }}
          transition={{ duration, repeat: Infinity, delay: i * (duration / coins.length), ease: "linear" }}
        >
          <CoinIcon />
        </motion.div>
      ))}
    </>
  );
};

// --- Main App Component ---
function App() {
  const [isPaused, setIsPaused] = useState(null);
  const [sentimentScore, setSentimentScore] = useState(0);
  const [tweets, setTweets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const mockAbi = (await import('./mock_abi.json')).default;
        const oracleAbi = (await import('./abi.json')).default;
        const provider = new ethers.JsonRpcProvider(ALCHEMY_API_URL);

        const contract = new ethers.Contract(MOCK_DEFI_ADDRESS, mockAbi, provider);
        console.log("Fetching paused status...");
        const status = await contract.paused();
        setIsPaused(status);
        console.log("Status fetched:", status);
        
        const oracleContract = new ethers.Contract(SENTIMENT_ORACLE_ADDRESS, oracleAbi, provider);
        console.log("Fetching latest timestamp from oracle...");
        const latestTimestamp = await oracleContract.latestTimestamp();
        
        if (Number(latestTimestamp) === 0) {
          throw new Error("No data has been submitted to the oracle yet. Run the Python agent.");
        }

        console.log("Fetching IPFS hash for the latest timestamp...");
        const ipfsHash = await oracleContract.getSentiment(latestTimestamp);

        if (ipfsHash) {
          const ipfsUrl = `https://ipfs.io/ipfs/${ipfsHash}`;
          const response = await fetch(ipfsUrl);
          const data = await response.json();
          setSentimentScore(data.average_sentiment);
          setTweets(data.detailed_results);
        } else {
           throw new Error("IPFS hash found was empty.");
        }

      } catch (error) {
        console.error("Error fetching data:", error);
        setTweets([{text: error.message}]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const getScoreColorClass = () => {
    if (isLoading) return 'score-yellow';
    if (sentimentScore > 0.3) return 'score-green';
    if (sentimentScore < -0.3) return 'score-red';
    return 'score-yellow';
  };

  return (
    <motion.div className="app-container" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1.5 }}>
      <TweetTicker tweets={tweets} />
      
      <div className="header">
        <h1>DeFi Sentinel</h1>
        <p>Real-time Market Sentiment Analysis for Risk Management</p>
      </div>
      
      <motion.div className="hud" initial={{ y: -100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.8, delay: 0.5 }}>
         <div className="score-display">
          <span>Sentiment Score</span>
          <span className={`score-value ${getScoreColorClass()}`}>
            {isLoading ? '----' : sentimentScore.toFixed(4)}
          </span>
        </div>
      </motion.div>

      <div className="animation-canvas">
        {!isPaused && !isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <CoinFlow CoinIcon={FaBitcoin} color="#f7931a" xStart={-400} xEnd={0} />
            <CoinFlow CoinIcon={FaDollarSign} color="#27ae60" xStart={0} xEnd={400} />
          </motion.div>
        )}

        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ duration: 0.8, type: 'spring', stiffness: 100 }}>
          <FaUniversity className="bank-icon" />
        </motion.div>

        <div className="status-text-container">
          <motion.div
            key={isPaused ? 'paused' : 'operational'}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <p className={isPaused ? 'status-paused' : 'status-operational'}>
              {isLoading ? "INITIALIZING..." : (isPaused ? "SYSTEM PAUSED" : "OPERATIONAL")}
            </p>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

export default App;

