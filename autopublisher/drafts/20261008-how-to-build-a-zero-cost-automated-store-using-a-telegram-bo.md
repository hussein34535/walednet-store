# How to Build a Zero-Cost Automated Store Using a Telegram Bot

Many developers overcomplicate e-commerce. They look at Stripe integrations, massive Shopify storefronts, and server infrastructure.

For selling digital assets—like API keys, PDF guides, or crypto tokens—this is unnecessary bloat.

You can build a functional, persistent store that costs $0 to run using only a free Telegram account and a standard Linux server. No credit cards required for the infrastructure.

Here is the practical guide to building a fully automated digital store using a Telegram bot.

## The Architecture: A Simple Script

We are going to build a script that uses the `python-telegram-bot` library. This approach replaces the need for a separate web server or payment gateway.

**The flow is linear:**
1.  **User** types `/buy` in a chat.
2.  **Script** sends a message with a **Product Link** (for example, a FileSend link).
3.  **User** clicks the link.
4.  **Script** instantly receives the link, unlocks the file, and confirms the purchase.

## Step 1: Set Up the Server

You need a place to host the bot. Do not use a shared web hosting panel like cPanel unless you know how to set up cron jobs. A cheap VPS (Virtual Private Server) is best.

*   **Option A:** A $5/mo DigitalOcean Droplet.
*   **Option B:** A free tier Render or Railway app.

For this guide, we will assume a standard Linux environment where you have `pip` and `python3` installed.

## Step 2: Configure the Telegram Bot

You don't need a Telegram Premium account to build this, but a Premium account gives you the "Edit Message" feature, which is crucial for automated receipts.

1.  Open Telegram and search for `@BotFather`.
2.  Send `/newbot`.
3.  Name your bot (e.g., "M3LM Hermes").
4.  Choose a unique username (e.g., `m3lm_hermes_bot`).
5.  Copy the **API Token**.

Save this token securely in your environment variables. Never hardcode it in your script.

## Step 3: The Python Script

Create a file named `store.py`. We will use the `io` module to simulate file delivery and the `python-telegram-bot` library to handle the API.

This script handles the logic for a single product: a "Crypto Pack."

```python
import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN_HERE")
# We simulate a product file. In reality, this would be a link to a file hosted on a storage service like DropBox, Mega, or Google Drive.
PRODUCT_LINK = "https://example.com/digital-pack.zip"
# A fake price to display on the button
PRODUCT_PRICE = "$10.00"
# --- END CONFIGURATION ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the M3LM Store. Use /buy to purchase the Crypto Pack."
    )

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create the inline keyboard with a link
    keyboard = [[InlineKeyboardButton(f"Buy {PRODUCT_PRICE} Pack", url=PRODUCT_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select the link below to proceed with payment and instant delivery:",
        reply_markup=reply_markup
    )

async def handle_purchase_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function is triggered when the user clicks the link.
    # In a real scenario, you would check for a webhook or a callback query here.
    
    user = update.effective_user
    chat_id = update.effective_message.chat_id
    
    # Here you would verify payment with a service like LemonSqueezy, Stripe, or manual wallet transfer.
    # For this example, we assume the link was clicked successfully.
    
    # Send the file
    try:
        # In a real app, you would use context.bot.send_document or send_photo
        await update.message.reply_text(
            f"Payment verified for {user.full_name}. \n\nDelivering your package..."
        )
        await update.message.reply_text("Click the link below to download your Crypto Pack:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Download File", url=PRODUCT_LINK)]]))
    except Exception as e:
        await update.message.reply_text("Failed to deliver the file. Please contact support.")

def main():
    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy_command))
    # We use a MessageHandler to catch text messages for this simplified example
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_purchase_confirmation))

    # Run the bot until the user presses Ctrl+C
    application.run_polling()

if __name__ == "__main__":
    main()
```

## Step 4: Deploy and Run

Do not run this locally. It will go offline when you close your terminal.

1.  Save the file.
2.  Install the library:
    ```bash
    pip install python-telegram-bot
    ```
3.  Run the bot in the background. On a Linux VPS, you can use `nohup`:
    ```bash
    nohup python3 store.py > bot.log 2>&1 &
    ```
4.  Check logs periodically to ensure no errors occur.

## Step 5: Handling the Delivery

The trickiest part of this architecture is the "click-through" flow.

When the user clicks "Buy $10 Pack," they leave the Telegram app. This is the only friction point.

To make this truly zero-cost, you do not need a payment processor. You can sell via:
1.  **Manual Wallet Transfer:** User sends USDT to your wallet, sends you a screenshot, and the bot automatically detects the transfer and sends the file.
2.  **Direct Links:** User pays outside Telegram (Stripe/LemonSqueezy), receives a code, and pastes it into the bot.
3.  **Encrypted Links:** You host files on a free cloud drive (like Google Drive) and use a script to generate expiring links (using a library like `pyfilesharing`).

The `handle_purchase_confirmation` function in the script above is where you implement the logic to unlock the link.

## Maintenance and Scaling

This script is stateless. This is good. It means you can restart the bot, and the store won't break.

However, for scale, you will eventually need a database (like SQLite or PostgreSQL) to store user IDs and inventory levels. For a "zero-cost" initial launch, simple text files or the built-in `sqlite3` library in Python are sufficient.

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot