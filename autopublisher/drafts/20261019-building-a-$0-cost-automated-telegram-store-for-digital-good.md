# Building a $0-Cost Automated Telegram Store for Digital Goods

Running an automated store isn't just about having a website. It’s about removing friction. If you sell digital packs, code snippets, or APIs, your customer should receive the download link instantly—without asking a human to email it to them.

You don't need a Stripe account, a Shopify theme, or a backend server with Docker containers. You can build a functioning automated shop using a free tier cloud server (like Render or Railway) and a Telegram bot.

Here is the practical workflow to build a store that costs roughly $5/month in hosting.

## 1. The Architecture: No Payment Gateway Required

Since this is a "free" project, we must avoid standard payment gateways (Stripe/PayPal). Instead, we will use a **deposit model**.

*   **How it works:** The user buys "Credits" via a peer-to-peer method (like crypto or local transfer).
*   **The Flow:**
    1.  User finds a product in your Telegram bot.
    2.  User pays you (e.g., via USDT TRC20).
    3.  User sends the transaction hash to the bot.
    4.  Your backend checks the blockchain.
    5.  **If found:** Bot unlocks the file/link.
    6.  **If not found:** Bot asks for payment.

This removes 100% of chargeback risk and platform fees, keeping your margins high.

## 2. Set Up the Telegram Bot

You don't need the `python-telegram-bot` library for this specific implementation. For a lean, $0-cost solution, use the **official Telegram Bot API** directly via **cURL**.

Create your bot via the [BotFather](https://t.me/BotFather) and get your `TOKEN`.

## 3. The Backend: Using a Free Platform

Don't host this on your laptop. Use a free tier from **Render.com** or **Railway.app**. These support Node.js and Python.

We will use **Express.js** (Node) for the server and **Binance API** (or TRC20 network API) to verify payments.

### The Code: Payment Verification & File Delivery

Here is a minimal example using Express. When a user types `/buy pack1`, the bot requests a payment address. When the user sends the transaction ID, this script checks the blockchain and delivers the link.

```javascript
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// 1. CONFIGURATION
const BOT_TOKEN = 'YOUR_BOT_TOKEN';
const API_URL = `https://api.telegram.org/bot${BOT_TOKEN}`;
const MY_WALLET_ADDRESS = 'YOUR_TRC20_ADDRESS';

// 2. DATA STORE (In a real app, use a DB like MongoDB or Supabase)
const products = {
  'premium_api': { price: 10, title: 'Premium API Pack', link: 'http://mysite.com/file.zip' },
  'source_code': { price: 25, title: 'Source Code Bundle', link: 'http://mysite.com/source.zip' }
};

let pendingPayments = {}; // Store pending transactions

// 3. ROUTES
app.post('/webhook', async (req, res) => {
  const message = req.body.message;
  if (!message) return res.send('');

  const chatId = message.chat.id;
  const text = message.text;

  // Handle Product Request
  if (text === '/start') {
    await sendMessage(chatId, "Welcome. Use /buy <code>premium_api</code> or /buy <code>source_code</code>");
  }

  if (text.startsWith('/buy ')) {
    const key = text.split(' ')[1];
    const product = products[key];

    if (product) {
      await sendMessage(chatId, `Buying ${product.title} costs $${product.price}. Send me a USDT (TRC20) payment for this amount to my wallet: ${MY_WALLET_ADDRESS}`);
      pendingPayments[chatId] = { key: key, price: product.price };
    }
  }

  // Handle Transaction Hash
  if (pendingPayments[chatId]) {
    const txHash = text;
    // Check Transaction on Binance API
    const status = await checkTransaction(txHash, pendingPayments[chatId].price);

    if (status) {
      // DELIVER PRODUCT
      const product = products[pendingPayments[chatId].key];
      await sendMessage(chatId, `✅ Payment Verified! Here is your download: ${product.link}`);
      delete pendingPayments[chatId];
    } else {
      await sendMessage(chatId, "❌ Payment not found or amount incorrect. Please try again.");
    }
  }

  return res.send('ok');
});

// HELPER FUNCTIONS
async function sendMessage(chatId, text) {
  await axios.post(`${API_URL}/sendMessage`, {
    chat_id: chatId,
    text: text,
    parse_mode: 'HTML'
  });
}

async function checkTransaction(hash, amount) {
  // Example: Fetch transaction details from Binance API or BscScan
  // Note: You need to implement the actual API call to verify the USDT amount
  // This is a placeholder for the logic
  return true; 
}

app.listen(process.env.PORT || 3000);
```

## 4. The "Zero-Cost" Infrastructure

To keep this running at $0 cost, you cannot use a complex database.

1.  **Database:** Use **Supabase** (free tier) or **FireStore**. Alternatively, for a very small scale, stick to the `pendingPayments` object in memory (works as long as the server doesn't restart).
2.  **File Hosting:** Use **Google Drive** or **Dropbox** public folders. Do not host the files on your backend server unless they are tiny.
3.  **SSL:** Render and Railway automatically handle HTTPS certificates for your webhook URL.

## 5. Verification Logic (The Tricky Part)

To make this work, you must write a script that checks the blockchain.

*   **For USDT TRC20:** Use the [Binance API](https://binance-docs.github.io/apidocs/spot/en/#trade-get-wallet-address) or a public TRC20 explorer API.
*   **For BSC/ETH:** Use [BscScan](https://bscscan.com/apis) or [Etherscan](https://docs.etherscan.io/).

Your `checkTransaction` function should look like this in practice:

```javascript
// Simplified logic to verify TRC20 transaction
async function checkTransaction(txHash, expectedAmount) {
  try {
    // Example using a public RPC node or API
    const response = await axios.get(`https://api.bscscan.com/api?module=transaction&action=gettxinfo&txhash=${txHash}&apikey=YOUR_API_KEY`);
    
    if (response.data.status === "1" && parseFloat(response.data.result.amount) >= expectedAmount) {
      return true;
    }
  } catch (e) {
    console.error(e);
  }
  return false;
}
```

## 6. Deploying

1.  Create a repository on GitHub.
2.  Push the code.
3.  Connect your repository to **Render.com** (or Railway).
4.  Render will give you a URL (e.g., `https://my-bot.onrender.com`).
5.  Go to **BotFather** on Telegram and set your webhook to:

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot