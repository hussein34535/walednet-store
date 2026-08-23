# Delivering Digital Files Without a Backend

I recently built a small marketplace for texture packs for designers. The goal was simple: sell files instantly after payment, without setting up a Node.js server, writing API routes, or dealing with complex databases.

If you want to deliver zip files, PDFs, or code snippets automatically, you don't need a backend. You can do this entirely from your frontend or serverless functions by leveraging the way HTTP responses work.

Here is the practical reality of how to make this happen.

## The Core Concept: Custom Content Disposition

When a user requests a file, your server sends back binary data. By default, browsers try to render that data as HTML, CSS, or text. To force a browser to download the file instead of opening it, you need to change the `Content-Disposition` header.

This header tells the client: "Don't display this, save it to disk."

In a standard Node.js server, this is how you set it up. You tell the system that the response is a "attachment" (download) and name the file whatever you want.

```javascript
// Express.js example
res.setHeader('Content-Disposition', 'attachment; filename=my-assets.zip');
res.sendFile('/path/to/file.zip');
```

This is the foundation of the entire operation. The file still exists on your server, but the "handling" logic happens without a backend API to process the payment logic first.

## Connecting the Payment Gateway

You cannot rely solely on a static link because you cannot monetize a static link. You need a transaction trigger.

The industry standard for this is Stripe. Stripe handles the payment, security, and webhook events.

1.  Create a product in Stripe (e.g., "UI Kit").
2.  Generate a checkout link using Stripe API.
3.  Include the URL of your file as a "success_url" parameter.

When the user completes the payment, Stripe redirects them to your success page.

This creates a dependency problem: your server doesn't know if the user actually paid unless you poll Stripe's API or listen to a webhook. Since we are doing this without a backend, we rely on a client-side trigger.

## The Frontend Logic (Client-Side Fetch)

You need a way to verify the payment from the user's browser.

This approach works best if you use a webhook for verification on the server side, but for a "no backend" implementation, you can use Stripe's API client in the browser.

You ask Stripe if this session ID is paid. If it is, you fetch the file.

**Step 1: Verify Payment Status**
```javascript
const stripe = Stripe('YOUR_PUBLIC_KEY');
const session = await stripe.checkout.sessions.retrieve(sessionId);

if (session.payment_status === 'paid') {
    // Proceed
}
```

**Step 2: Fetch the File**
Once you have confirmed payment, you use the browser's `fetch` API to grab the binary data.

```javascript
const response = await fetch('https://your-domain.com/dl/file.zip');
const blob = await response.blob();

// Create a temporary link to trigger download
const link = document.createElement('a');
link.href = window.URL.createObjectURL(blob);
link.download = 'my-assets.zip';
link.click();
```

This approach is fully client-side. It requires no server-to-server communication for the file transfer, making it incredibly cheap and fast.

## Handling Security and Permissions

The biggest risk here is that if the download link is guessable, anyone can get the file for free.

You must obscure the download URL.

1.  **Hash the file path**: Instead of `files/asset.zip`, use a random hash like `files/a1b2c3d4.zip`.
2.  **Map hash to ID**: On your server (or a static site generator like Hugo), create a mapping file. This is just a JSON object: `{ "a1b2c3d4": "file.zip" }`.
3.  **Serve the JSON**: When a user requests a hash, you read the JSON to find the real filename.
4.  **Deliver the File**: If the hash exists and the user has paid, serve the real file with the `Content-Disposition` header.

If someone guesses the hash, they only get an error or a 404. They cannot find the file.

## Static Site Considerations

If you are building this on a platform like Netlify or Vercel, you can achieve this by configuring your `netlify.toml` file.

You can set up a rewrite rule that intercepts requests to `/dl/*`. This rule points to a function that serves the file based on the request parameter. Because Vercel/Netlify Functions are serverless, you still have access to the `res.setHeader` logic discussed earlier.

This keeps your infrastructure costs at zero while maintaining the security of a dynamic system.

## The Result

You now have a system where:
*   **Stripe** handles the money.
*   **A client-side script** verifies the payment.
*   **A browser fetch** delivers the binary blob.
*   **A serverless function** serves the file with the correct headers.

This method is robust enough for thousands of micro-transactions and requires zero maintenance of a database. It moves the complexity from your backend to the frontend layer, where the browser handles the heavy lifting.

---
I sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: https://t.me/m3lmhermes_bot