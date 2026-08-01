# WaledNet Store — Auto Publisher

Free acquisition pipeline for the WaledNet digital-products Telegram store.

## What's inside

| Path | Purpose |
|---|---|
| `autopublisher/article_generator.py` | Generates a fresh SEO article (600-900 words) via ZenMux AI and publishes it to Dev.to. Saves a draft copy to `drafts/` on every run. Free model by default (`z-ai/glm-4.7-flash-free`), auto-fallback to `deepseek/deepseek-v4-flash`. |
| `autopublisher/.github/workflows/publish-devto.yml` | GitHub Actions: runs the generator every day at 06:00 UTC (manual "Run workflow" button also works). |
| `autopublisher/pin_maker.py` | Generates 15 branded Pinterest pin images (1000x1500) from `pinterest/pins.md` using Pillow. Run locally: `python pin_maker.py`. |
| `autopublisher/pinterest/` | Keywords, 15 ready pin copies (title/description/board/image text) and image prompts. |
| `product/landing.html` | Static landing page — deploy to Cloudflare Pages (free) and use it as the funnel link for pins/articles. |

## Required secrets (repo Settings → Secrets and variables → Actions)

- `ZENMUX_KEY` — AI API key (value: in `D:\GOAL_DOLLAR\autostore\config.json` on the owner's machine)
- `DEVTO_KEY` — Dev.to API key (same file: `devto_key`)

## How it works

1. At 06:00 UTC GitHub Actions starts (GitHub's IP is allowed by Dev.to — the owner's home IP is blocked, hence Actions).
2. The script picks a topic never used before (`published_topics.txt`), generates the article, publishes it, commits the draft + history back to the repo.
3. Every article ends with a soft CTA pointing to `https://t.me/m3lmhermes_bot`.

Local testing (no publish): `python autopublisher/article_generator.py` — saves draft only.
