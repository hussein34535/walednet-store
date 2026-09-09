# How to Build a Zero-Cost Automated Store With a Telegram Bot

Developers often look at automated sales pipelines and assume they require expensive infrastructure: dedicated servers, managed databases, payment gateways, and inventory management systems. However, you can build a functioning store that sells digital assets—such as vouchers, access keys, or crypto—and delivers them instantly, all without spending a single dollar on infrastructure.

Here is the practical guide to building this system using existing free tools.

### 1. The Architecture: No Servers, Just APIs

The goal is to eliminate the "middleman." Instead of hosting a website and a database, you will act as a single-point-of-contact: the bot. When a user wants to buy a product, they interact with your Telegram bot. The bot checks its memory (a simple database), processes the request, and sends the product file instantly.

For this to work, you need two main components:
1.  **A Bot:** To handle user input and file delivery.
2.  **A Storage Method:** To hold your product files and manage user purchases.

### 2. Setting Up the Database: JSON Bin

You do not need to spin up a PostgreSQL or MongoDB instance. Use a free, persistent JSON storage service.

I recommend **JSON Bin**. It provides a free tier (up to 10MB) that allows you to store JSON documents with auto-expiry. We will use it to store two things:
*   **Inventory:** The list of products available.
*   **Purchases:** A mapping of User ID -> Product Key.

Create a new Bin and copy the API Key and Bin ID. We will use Node.js to interact with it.

### 3. The Bot Logic in Node.js

We will use the `node-telegram-bot-api` library. It is lightweight, handles webhooks automatically, and is perfect for bots that simply send files.

**Step 1: Install dependencies**
```bash
npm install node-telegram-bot-api axios
```

**Step 2: The Bot Code**
Copy your JSON Bin URL. Replace the placeholder with your actual Bin ID.

```javascript
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const token = process.env.TELEGRAM_TOKEN; // Set token as env var
const binId = 'YOUR_JSON_BIN_ID';
const apiKey = 'YOUR_JSON_BIN_API_KEY';

const bot = new TelegramBot(token, { polling: true });

// Helper to fetch inventory
async function getInventory() {
    const res = await axios.get(`https://api.jsonbin.io/v3/b/${binId}`);
    return res.data.record;
}

// Helper to save purchases
async function savePurchase(userId, productId) {
    // Fetch current data
    let data = await getInventory();
    
    // Check if user already has this item
    if (data.purchases && data.purchases[userId] && data.purchases[userId].includes(productId)) {
        return;
    }

    // Add to purchases
    if (!data.purchases) data.purchases = {};
    if (!data.purchases[userId]) data.purchases[userId] = [];
    
    data.purchases[userId].push(productId);
    
    // Update Bin
    await axios.put(`https://api.jsonbin.io/v3/b/${binId}/latest`, data, {
        headers: { 'X-Master-Key': apiKey }
    });
}

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "Welcome to the store. Use /buy [product_id] to purchase.");
});

bot.onText(/\/buy (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const productId = match[1];

    // 1. Fetch Inventory
    const inventory = await getInventory();
    const product = inventory.items.find(item => item.id === productId);

    if (!product) {
        return bot.sendMessage(chatId, "Product not found.");
    }

    // 2. Check if already bought
    const purchaseKey = `${chatId}_${productId}`;
    if (inventory.purchases && inventory.purchases[chatId] && inventory.purchases[chatId].includes(productId)) {
        return bot.sendMessage(chatId, "You have already purchased this item.");
    }

    // 3. Send the file
    // You can use URL or upload a local file
    try {
        await bot.sendDocument(chatId, product.fileUrl, { caption: `Here is your ${product.name}.` });
        
        // 4. Mark as sold
        await savePurchase(chatId, productId);
        
        bot.sendMessage(chatId, "Order processed successfully.");
    } catch (err) {
        bot.sendMessage(chatId, "Failed to send file.");
    }
});
```

### 4. Handling Payments: The Human Element

This is the most critical part of a zero-cost store. Since you are not integrating Stripe or PayPal, you have no automated fraud protection.

**How to receive payment:**
*   **Direct Transfers:** Ask users to send a payment via USDT (TRC20 or BEP20) or crypto directly to your wallet.
*   **Payment Links:** Use services like XUMM or instant payment links (where available in your region) and provide the link in the bot.

**Verification Workflow:**
1.  User says `/buy item_123`.
2.  Bot replies: *"Please send 10 USDT to this address: [Your Address]. Send a screenshot to complete the order."*
3.  You (or an automated script if you are advanced) verify the transaction on the blockchain and press the `/buy item_123` command (or send a "Paid" command) to the bot.
4.  Bot detects the "Paid" trigger and sends the file.

*Note: This manual step relies on your trust or reputation. To automate this, you would need a bot that monitors the blockchain for your address, but that introduces complexity and gas fees.*

### 5. Scaling to Production

The code above works perfectly for a side project. To make it robust for multiple users:

1.  **Environment Variables:** Never hardcode keys. Use `dotenv`.
2.  **File Storage:** If you cannot host files publicly, you can upload files directly from your local machine to Telegram using `bot.sendDocument`.
3.  **Concurrency:** The `node-telegram-bot-api` handles concurrent requests well, but if you scale to thousands of users, you will eventually hit JSON Bin rate limits. At that point, you would need to move to a proper database like Firebase or Supabase.

### 6. Security and Privacy

Since you are using Telegram, you have a layer of encryption. However, treat user data responsibly. Do not log private messages. Ensure your JSON Bin keys are secure. If you are selling sensitive items, consider implementing a token system: The bot sends a key, and the user must verify it on a website to unlock the actual content.

---

I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot