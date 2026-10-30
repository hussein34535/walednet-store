# Build a $0-Cost Automated Store with a Telegram Bot: A Practical Guide

Selling digital products doesn't require Shopify, WooCommerce, or Stripe subscriptions. You can run a functional e-commerce operation entirely from your laptop using Telegram and your existing web hosting.

This guide focuses on a specific, high-volume model: selling packs of pre-made credentials (e.g., social media accounts) or simple digital assets. We will build this using a Telegram Bot, a Node.js backend, and a shared server.

### The Architecture

We will implement a flow that requires zero maintenance from you after deployment:

1.  **User Interaction:** A Telegram bot receives a message with the product code (e.g., `/buy_1`).
2.  **Payment:** The bot returns a crypto wallet address for the user to send payment.
3.  **Processing:** The user sends the payment receipt.
4.  **Delivery:** The bot verifies the transaction on-chain, then automatically sends the product file to the user.

This avoids the complexity of Stripe and integrates perfectly with crypto payments.

### Step 1: The Development Environment

Create a new project folder and initialize a Node.js application.

```bash
mkdir telegram-store
cd telegram-store
npm init -y
npm install express axios telegraf dotenv
```

*   `express`: To run a simple web server.
*   `axios`: To make HTTP requests to block explorers.
*   `telegraf`: The robust framework for handling Telegram bot logic.
*   `dotenv`: To manage your API keys securely.

Create a `.env` file in the root directory:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
PORT=3000
COIN_SYMBOL=USDT
```

### Step 2: The Bot Logic

Create a file named `server.js`. This script handles the bot logic.

We need a simple inventory system. For this example, we will use an array of objects representing available products.

```javascript
const { Telegraf } = require('telegraf');
const express = require('express');
require('dotenv').config();

const bot = new Telegraf(process.env.BOT_TOKEN);
const app = express();
app.use(express.json());

// Inventory: ID, Price in Crypto, File URL (or path)
const products = [
  { id: '1', name: 'Instagram Pack', price: 10, link: 'https://example.com/file.zip' },
  { id: '2', name: 'Twitter Pack', price: 15, link: 'https://example.com/file.zip' }
];

// User state management
// Keys are user IDs, values are objects containing current state and cart
const sessions = {};

bot.start((ctx) => ctx.reply('Welcome! Send /buy_1 to purchase the first pack.'));

// Command to buy
bot.command('buy_1', (ctx) => {
  const userId = ctx.from.id;
  sessions[userId] = { step: 'awaiting_payment', productId: '1' };
  ctx.reply(`Select payment method: Send a screenshot of USDT sent to: \`0x...\``);
  ctx.replyWithMarkdown(`\`0x123...abc\` (10 ${process.env.COIN_SYMBOL})`);
});

// Handle incoming text messages (payment receipts)
bot.on('text', async (ctx) => {
  const userId = ctx.from.id;
  const userSession = sessions[userId];

  if (!userSession) return; // Ignore messages from users not in the store flow

  if (userSession.step === 'awaiting_payment') {
    // 1. Verify Payment (Simplified Logic)
    // In a real scenario, you would verify the hash on a blockchain explorer.
    // For this demo, we simulate the delay.
    
    ctx.reply('Processing payment... please wait.');
    
    // Simulate async processing
    setTimeout(async () => {
      try {
        // 2. Send Product
        const product = products.find(p => p.id === userSession.productId);
        await ctx.reply('Payment Verified!');
        await ctx.replyWithPhoto({ source: 'path/to/proof.jpg' }); // Optional: Proof of purchase
        await ctx.replyWithDocument({ source: product.link });
        delete sessions[userId]; // End session
      } catch (error) {
        ctx.reply('Error delivering the file.');
        delete sessions[userId];
      }
    }, 3000);
  }
});

// Start the bot
bot.startPolling();

// Start the Express server
app.listen(process.env.PORT, () => {
  console.log(`Server running on port ${process.env.PORT}`);
});
```

### Step 3: Hosting for $0

Do not pay for VPS providers like DigitalOcean or AWS. You need a server with a public IP address.

1.  **Get a Free VPS:** Sign up for **Render.com** (supports Node.js), **Railway.app**, or **Fly.io**. These platforms often offer a free tier that lasts 6 months.
2.  **Deploy:** Push your code to GitHub and connect the repository to your hosting provider. Render will automatically detect `package.json`, install dependencies, and run `node server.js`.

### Step 4: The "Glue" (Optional but Recommended)

Running a bot solely on a single server with one user connection can sometimes result in timeouts. To make it robust, use **ngrok** to tunnel your local port to the internet, or set up a proper server configuration.

If you are using Render, simply ensuring your code listens on `process.env.PORT` is usually sufficient for a low-traffic store.

### Managing Risks

This model is high-risk regarding ToS (Terms of Service) and legal compliance.

*   **File Hosting:** You cannot use your free hosting account's storage for sensitive files. Use a dedicated file storage service like Dropbox, Google Drive (with sharing links), or a cheap CDN. If your free hosting quota is reached, the bot stops working.
*   **Bans:** Telegram will ban bots that do not respond to users. Ensure your code includes error handling so the bot remains online even if one user's payment fails.

### Conclusion

You now have the code and the workflow to automate a digital store. The barrier to entry is the code, not the infrastructure. By using Telegram's native API, you reduce friction for the buyer and eliminate transaction fees.

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot