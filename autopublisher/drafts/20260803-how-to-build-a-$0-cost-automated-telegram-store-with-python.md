# How to Build a $0-Cost Automated Telegram Store with Python and a Crypto Wallet

Building an automated e-commerce store is usually associated with massive upfront costs, hosting fees, and complex inventory management systems. If you are a developer or freelancer looking to sell digital products (codes, crypto, access keys), you don't need a $20/mo Shopify subscription.

You can build a fully functional, self-hosted store using only a Telegram bot and a lightweight script. This guide walks through the technical implementation of a "pay-for-code" flow using Python, the `aiogram` library, and a crypto wallet API.

## Prerequisites: The $0 Stack

To keep costs at zero, we rely on free tools and open-source libraries.

1.  **Runtime:** Python 3.8+ (install via [python.org](https://www.python.org/)).
2.  **Bot Framework:** `aiogram 3.x` (a robust asynchronous library for Telegram bots).
3.  **Payment Gateway:** A crypto wallet API (e.g., [Coinbase Commerce](https://commerce.coinbase.com/) or [PayPal REST API](https://developer.paypal.com/)).
4.  **Hosting:** A free tier (Railway, Render, or a local VPS) or simply run it locally on your machine.

## Step 1: Setting Up the Telegram Bot

Start by creating a bot with [@BotFather](https://t.me/BotFather) in Telegram. Save the API token it provides.

Create a Python file named `store_bot.py` and install the necessary library:

```bash
pip install aiogram
```

Connect the bot to the Python script. We will implement a simple command to list products.

```python
import asyncio
from aiogram import Bot, Dispatcher, types

TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# In a real app, fetch this from a database
PRODUCTS = {
    "101": {"title": "Python Script Pack", "price": 5.00, "currency": "USD"},
    "102": {"title": "Access Key: DevTools Pro", "price": 2.50, "currency": "USD"},
}

@dp.message(commands=["start", "menu"])
async def send_menu(message: types.Message):
    msg = "Welcome to the automated store.\nChoose a product by ID:\n"
    for pid, p in PRODUCTS.items():
        msg += f"[{pid}] {p['title']} - ${p['price']}\n"
    
    await message.answer(msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 2: Integrating a Payment Gateway (The Logic)

The store functionality relies on generating a payment link when a user selects a product.

For a $0-cost solution, we will simulate the payment integration using a logic flow typical of crypto payments. When a user types the product ID (e.g., "101"), the bot generates a unique payment request ID and returns a "Pay Now" link.

```python
import secrets
import time

# Simulating an external payment provider response
# In production, replace this with a call to Coinbase Commerce / PayPal API
def process_payment(product_id, user_id):
    # 1. Generate a unique transaction ID
    tx_id = secrets.token_hex(4)
    
    # 2. Simulate payment processing delay
    time.sleep(2)
    
    # 3. Return a mock "Payment URL" and Transaction ID
    return {
        "success": True,
        "payment_url": f"https://example-pay.com/pay/{tx_id}",
        "tx_id": tx_id,
        "product_id": product_id
    }

@dp.message()
async def handle_product_selection(message: types.Message):
    # Check if the user input is a valid product ID
    if message.text not in PRODUCTS:
        await message.answer("Invalid ID. Type /menu to see products.")
        return

    product_id = message.text
    product = PRODUCTS[product_id]

    # Send an order prompt
    await message.answer(
        f"You selected: {product['title']} (${product['price']})\n"
        f"Please click the link below to complete the payment:\n"
        f"http://localhost:3000/checkout?pid={product_id}"
    )
```

## Step 3: Automated Delivery (The "Magic")

This is the critical part: automation. When the payment gateway confirms a successful transaction, the bot must immediately deliver the product to the user without human intervention.

We add a listener to the dispatcher that watches for specific messages (webhooks from your payment provider) or polls a database for completed payments.

```python
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class PaymentState(StatesGroup):
    waiting_for_payment = State()

@dp.message(PaymentState.waiting_for_payment)
async def handle_payment_confirmation(message: types.Message):
    # In a real scenario, this data comes from the payment webhook
    # For this example, assume the provider sends a success message
    tx_id = message.text
    
    # Find which product was purchased (usually stored in session or DB)
    # Assuming we looked up the product_id earlier
    product_id = "101" 
    
    if product_id in PRODUCTS:
        product = PRODUCTS[product_id]
        
        # DELIVER THE PRODUCT
        delivery_text = (
            f"✅ Payment Confirmed!\n"
            f"Here is your code for {product['title']}:\n\n"
            f"DEMO-KEY-12345-ABCD\n\n"
            f"Save this key."
        )
        
        await message.answer(delivery_text)
    else:
        await message.answer("Payment verified, but product not found.")
```

## Step 4: Hosting and Scaling

If you want to sell to real customers, you can't run this script on your laptop 24/7.

1.  **Railway / Render:** Create a new Python project and push your code to GitHub. These platforms offer free tiers for small bot instances.
2.  **ngrok:** If running locally for testing, use ngrok to expose your localhost port to the internet so the payment provider can reach your bot.

## Managing Data and Keys

Since this is a $0-cost build, you cannot rely on expensive managed database tiers for long-term data storage.

*   **Session Management:** Use `aiogram.fsm.storage.redis` to keep track of user states.
*   **Database:** For a production store, set up a tiny PostgreSQL instance on Render or use a simple JSON file if traffic is low.
*   **API Keys:** Never hardcode your API keys in the script. Use environment variables (`os.getenv`).

## The "No-Code" Alternative

If you aren't comfortable writing the polling logic yourself, you can use a no-code automation tool like Zapier.

1.  Set up a Stripe or PayPal webhook.
2.  When payment is successful, Zapier triggers a Telegram bot message to the user containing their download link or code.
3.  Build a simple landing page (HTML/CSS) hosted on Netlify (free) to display the products.

This approach is less customizable than the Python script above but requires zero backend logic.

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot