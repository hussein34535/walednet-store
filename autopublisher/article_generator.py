import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE_DIR)
CFG_PATH = os.path.join(ROOT, "autostore", "config.json")
DRAFTS_DIR = os.path.join(BASE_DIR, "drafts")
DONE_PATH = os.path.join(BASE_DIR, "published_topics.txt")
LOG_PATH = os.path.join(BASE_DIR, "publisher.log")

ZENMUX_URL = "https://zenmux.ai/api/v1/chat/completions"
DEVTO_URL = "https://dev.to/api/articles"
TELEGRAPH_URL = "https://api.telegra.ph"
INDEXNOW_KEY = "walednetindex2026"
PAGES_HOST = "hussein34535.github.io"
PAGES_PATH = "/walednet-store/"
TELEGRAPH_TOKEN_FILE = os.path.join(BASE_DIR, "telegraph_account.json")

TOPICS = [
    "How to sell digital products online with zero ad budget in 2026",
    "The 3 easiest digital products to create and sell this month",
    "How to get your first paying freelancing client in 30 days",
    "AI prompts that save freelancers 10+ hours every week",
    "How to build a $0-cost automated store with a Telegram bot",
    "USDT vs PayPal for small online sellers: which to choose",
    "How to accept crypto payments in your small business for free",
    "5 micro-digital products anyone can sell from their phone",
    "Why creators fail at selling prompts (and how to fix it)",
    "A beginner's honest guide to selling on the internet in 2026",
    "How to deliver digital downloads automatically with no backend",
    "Selling ebooks and templates on autopilot: a practical setup",
    "How to price your first digital product without guessing",
    "What I learned running a store that never sleeps",
    "12 free tools to start selling online before you spend $1",
]

TAGS = ["productivity", "freelancing", "ai", "business"]

MODELS = [
    "z-ai/glm-4.7-flash-free",
    "deepseek/deepseek-v4-flash",
    "deepseek/deepseek-v4-flash-free",
]

BOT_LINK = "https://t.me/m3lmhermes_bot"

os.makedirs(DRAFTS_DIR, exist_ok=True)


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def load_done():
    try:
        with open(DONE_PATH, encoding="utf-8") as f:
            return [l.strip() for l in f.read().splitlines() if l.strip()]
    except OSError:
        return []


def save_done(topic):
    with open(DONE_PATH, "a", encoding="utf-8") as f:
        f.write(topic + "\n")


def pick_topic():
    done = load_done()
    remaining = [t for t in TOPICS if t not in done]
    pool = remaining or TOPICS
    return random.choice(pool)


def zenmux_call(key, prompt, max_tokens, temperature):
    errors = []
    for model in MODELS:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "thinking": {"type": "disabled"},
        }).encode()
        req = urllib.request.Request(
            ZENMUX_URL, data=payload,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
            text = d["choices"][0]["message"].get("content", "").strip()
            if text:
                return text, model
            errors.append(f"{model}: empty")
        except Exception as e:
            errors.append(f"{model}: {e}")
        time.sleep(2)
    log("zenmux: all models failed: " + " | ".join(errors))
    return None, None


def gen_article(cfg, topic):
    key = cfg.get("zenmux_key", "") or os.environ.get("ZENMUX_KEY", "")
    if not key:
        log("ERROR: no zenmux key (config.json or ZENMUX_KEY env)")
        return None
    prompt = (
        f'Write a genuine, practical markdown article (600-900 words) for developers and '
        f'freelancers on dev.to. Topic: "{topic}". '
        "Requirements: strong specific title, clear headings, short actionable paragraphs, "
        "real examples, zero spam, zero hype, zero fabricated numbers, no generic filler. "
        "Do not write a sales pitch. "
        "End the article with exactly this block:\n\n"
        "---\n"
        "I sell these kinds of digital packs in a tiny automated Telegram store - "
        "instant USDT delivery. Check it: " + BOT_LINK + "\n\n"
        "Output format: the title on its own first line starting with '# ', "
        "then the article body in markdown."
    )
    text, model = zenmux_call(key, prompt, 1600, 0.9)
    if not text:
        return None
    lines = text.split("\n")
    if lines[0].lstrip().startswith("#"):
        title = lines[0].lstrip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()
    else:
        title = topic
        body = text
    if "m3lmhermes_bot" not in body:
        body += "\n\n---\nI sell these kinds of digital packs in a tiny automated Telegram store - instant USDT delivery. Check it: " + BOT_LINK
    return title, body, model


def telegraph_ensure_token():
    try:
        with open(TELEGRAPH_TOKEN_FILE, encoding="utf-8") as f:
            tok = json.load(f).get("access_token")
            if tok:
                return tok
    except OSError:
        pass
    payload = json.dumps({"short_name": "walednet", "author_name": "WaledNet Store"}).encode()
    req = urllib.request.Request(
        TELEGRAPH_URL + "/createAccount", data=payload,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        if d.get("ok"):
            tok = d["result"]["access_token"]
            with open(TELEGRAPH_TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump({"access_token": tok}, f)
            log("telegraph: new account created")
            return tok
        log("telegraph: account error: " + str(d.get("error")))
    except Exception as e:
        log(f"telegraph: account error: {e}")
    return None


def md_to_nodes(body):
    nodes = []
    para = []
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            if para:
                nodes.append({"tag": "p", "children": [" ".join(para)]})
                para = []
        elif s.startswith("## "):
            if para:
                nodes.append({"tag": "p", "children": [" ".join(para)]})
                para = []
            nodes.append({"tag": "h2", "children": [s[3:]]})
        elif s.startswith("> "):
            nodes.append({"tag": "blockquote", "children": [s[2:]]})
        elif s == "---":
            if para:
                nodes.append({"tag": "p", "children": [" ".join(para)]})
                para = []
            nodes.append({"tag": "hr"})
        elif "m3lmhermes_bot" in s:
            before = s.split("m3lmhermes_bot")[0].rstrip(" -:") or "Open the store on Telegram"
            nodes.append({"tag": "p", "children": [
                before + " ",
                {"tag": "a", "attrs": {"href": BOT_LINK}, "children": [BOT_LINK]},
            ]})
        else:
            para.append(s)
    if para:
        nodes.append({"tag": "p", "children": [" ".join(para)]})
    return nodes


def telegraph_publish(title, body):
    tok = telegraph_ensure_token()
    if not tok:
        return None
    payload = json.dumps({
        "access_token": tok,
        "title": title,
        "author_name": "WaledNet Store",
        "content": md_to_nodes(body),
    }).encode()
    req = urllib.request.Request(
        TELEGRAPH_URL + "/createPage", data=payload,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        if d.get("ok"):
            url = d["result"]["url"]
            log(f"telegraph: published '{title}' -> {url}")
            return url
        log("telegraph: createPage error: " + str(d.get("error")))
    except Exception as e:
        log(f"telegraph: error: {e}")
    return None


def indexnow_submit(urls):
    payload = json.dumps({
        "host": PAGES_HOST,
        "key": INDEXNOW_KEY,
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
        log(f"indexnow: submitted {len(urls)} urls (status {code})")
    except Exception as e:
        log(f"indexnow: error: {e}")


def devto_publish(cfg, title, body):
    key = cfg.get("devto_key", "") or os.environ.get("DEVTO_KEY", "")
    if not key:
        log("ERROR: no devto key (config.json or DEVTO_KEY env)")
        return False
    payload = json.dumps({
        "article": {
            "title": title,
            "published": True,
            "body_markdown": body,
            "tags": TAGS[:4],
        }
    }).encode()
    req = urllib.request.Request(
        DEVTO_URL, data=payload,
        headers={
            "Content-Type": "application/json",
            "api-key": key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode())
        url = d.get("url", "?")
        log(f"devto: published '{title}' -> {url}")
        return True
    except Exception as e:
        log(f"devto: publish failed: {e}")
        return False


def main():
    publish = "--publish" in sys.argv
    cfg = load_json(CFG_PATH, {})
    topic = pick_topic()
    log(f"generating article for: {topic}")
    result = gen_article(cfg, topic)
    if not result:
        log("generation failed, nothing published")
        return 1
    title, body, model = result
    slug = title.lower().replace(" ", "-")[:60].strip("-")
    stamp = datetime.now().strftime("%Y%m%d")
    path = os.path.join(DRAFTS_DIR, f"{stamp}-{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{body}")
    log(f"saved draft: {path} (model={model})")
    if publish:
        urls = [f"https://{PAGES_HOST}{PAGES_PATH}"]
        ok = False
        if devto_publish(cfg, title, body):
            save_done(topic)
            log("topic marked as done")
            ok = True
        tg_url = telegraph_publish(title, body)
        if tg_url:
            urls.append(tg_url)
        if ok or tg_url:
            indexnow_submit(urls)
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
