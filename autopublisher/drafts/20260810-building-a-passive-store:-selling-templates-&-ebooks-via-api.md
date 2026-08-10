# Building a Passive Store: Selling Templates & Ebooks via API Without a Platform Fee

If you are a developer or freelancer, you already have a product: code, designs, or intellectual property. The problem isn't the idea; it is the friction of selling it.

Selling on platforms like Gumroad, Etsy, or even setting up your own WordPress store requires managing tax compliance, shipping, customer support tickets, and platform fees. It breaks the flow of coding.

Here is a practical setup to sell digital packs—ebooks, UI kits, or source code—using a Telegram bot and an automated API. This route offers near-zero fees and instant gratification for the buyer.

## Step 1: The "Customer" Infrastructure

Before building anything, you need a wallet that accepts crypto. We will use **TON (The Open Network)**.

*Why TON?* It has zero gas fees for sending transactions and is incredibly fast. It is perfect for instant delivery systems.

1.  Download the **Tonkeeper** or **Tonhub** wallet app on your phone.
2.  Create a wallet and copy your **Wallet Address**. You will need this address to receive payments from your bot.

## Step 2: The Telegram Bot (The Storefront)

You do not need a custom React app or a landing page with broken SSL certificates. A simple Telegram bot is all you need to handle payments and file delivery.

Use **@BotFather** on Telegram to create a new bot. Give it a name (e.g., "DevAssets Store"). Once created, save the **API Token** provided by BotFather.

## Step 3: The Payment API (The Payment Gateway)

This is the most critical step. You need an API that connects a Telegram command to a smart contract.

**Node.js Implementation:**

You will need a basic Node.js script. First, install the official Telegram bot library:

```bash
npm install node-telegram-bot-api
npm install ton-sdk
```

Here is a functional skeleton script. It listens for a command, sends a payment request, and waits for confirmation.

```javascript
const TelegramBot = require('node-telegram-bot-api');
const { WalletV4R2 } = require('ton-crypto');
const { TonClient, Cell, Address } = require('ton');

// 1. Configuration
const TOKEN = 'YOUR_BOT_TOKEN_FROM_BOTFATHER';
const WALLET_ADDRESS = 'YOUR_WALLET_ADDRESS'; // From Tonkeeper
const bot = new TelegramBot(TOKEN, { polling: true });
const client = new TonClient({ endpoint: 'https://toncenter.com/api/v2/jsonRPC' });

// 2. Helper to send a message
function sendMessage(chatId, text) {
    bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
}

// 3. Handle the /buy command
bot.onText(/\/buy/, async (msg) => {
    const chatId = msg.chat.id;
    const productId = "UI-KIT-PRO"; // Your product SKU

    sendMessage(chatId, `*Preparing ${productId} for purchase...*`);

    try {
        // Create a text memo that proves what the user is buying
        const message = `Purchase: ${productId} - Value: 5 USDT`;

        // NOTE: This is a simplified example.
        // In production, you must generate a proper wallet transaction 
        // and return the 'requestId' to the user to sign.
        // Many services like Helio or SimpleTON handle this complexity for you.
        
        sendMessage(chatId, `Please send 5 USDT to: ${WALLET_ADDRESS} with memo: ${message}`);
        
        // Logic to verify the transaction would go here 
        // (polling the blockchain for incoming transactions to that address)

    } catch (error) {
        console.error(error);
        sendMessage(chatId, "Error processing request.");
    }
});
```

**The "Secret Sauce":**
Writing raw crypto logic in Node.js is prone to errors (address formatting, wallet versioning, memo matching). Do not build a custom wallet signer if you can avoid it.

Instead, use a service like **SimpleTON** or **Helio**. These services generate a secure link. You send that link to the user via Telegram. The user clicks the link, approves the payment in their wallet app, and **you receive a webhook callback instantly**.

## Step 4: The Automation (The Deliverable)

When the payment webhook hits your server, your code should trigger a file transfer.

```javascript
// Pseudo-code for the webhook handler
app.post('/webhook', async (req, res) => {
    const { userId, amount, memo } = req.body;

    if (amount >= 5 && memo.includes('UI-KIT-PRO')) {
        // The asset file (URL or base64)
        const fileUrl = 'https://mysite.com/files/ui-kit-v1.zip';
        
        await bot.sendDocument(userId, fileUrl, {
            caption: "Thank you for your purchase. Here is your UI Kit."
        });
    }
    res.sendStatus(200);
});
```

This removes all manual work. You do not need a shopping cart, a checkout page, or a "thank you" email sequence.

## Why This Matters for Devs

1.  **Instant Gratification:** You don't have to wait for a bank transfer to clear. The file is sent in seconds.
2.  **Zero Marketplace Fees:** You keep 100% of the revenue. Platforms like Gumroad take a cut; you don't.
3.  **Tech Stack Flexibility:** You can sell JSON configs, CLI tools, or code snippets just as easily as PDF ebooks.

This setup turns your wallet into a vending machine. You build the product once; the API handles the rest.

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot