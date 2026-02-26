#!/usr/bin/env python3
"""
Daily AI News Brief
Fetches AI news from the web (matching Han's X AI + News list accounts),
synthesizes an executive summary using Claude, and emails it to han.choe88@gmail.com.
"""

import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from ddgs import DDGS

# ── Accounts in Han's X "AI + News" list ─────────────────────────────────────
AI_NEWS_ACCOUNTS = [
    "mlnchoi", "demishassabis", "aledge_", "sama", "OpenAI",
    "AnthropicAI", "GoogleAI", "NVIDIAAAI", "karpathy", "AndrewYNg",
    "petergyang", "rowancheung", "minchoi", "alliekmiller", "geoffreyhinton",
    "drfeifel", "ylecun", "AIBreakfast", "heyrobinai", "The_DailyAI",
    "DarioAmodei", "gdb", "ilyasut", "emollick", "ClementDelangue", "simonw",
    "levie", "heyrobinai", "godofprompt", "heyshrutimishra", "slow_developer",
    "chamath", "elonmusk",
]

RECIPIENT_EMAIL = "han.choe88@gmail.com"


# ── 1. Fetch News ─────────────────────────────────────────────────────────────

def fetch_ai_news() -> list[dict]:
    """Search DuckDuckGo for recent AI news relevant to the followed accounts."""
    ddgs = DDGS()
    all_results: list[dict] = []

    queries = [
        "AI model release announcement today",
        "OpenAI Anthropic Google DeepMind Meta AI news today",
        "artificial intelligence research breakthrough today",
        "AI policy regulation government news today",
        "large language model LLM news today",
        "AI startup funding product launch today",
        "DeepSeek Mistral Gemini Claude GPT news today",
        "AI agents tools developer news today",
    ]

    # General AI news searches
    for query in queries:
        try:
            results = list(ddgs.text(query, timelimit="d", max_results=6))
            all_results.extend(results)
        except Exception as e:
            print(f"  ⚠ Search skipped for '{query[:40]}...': {e}", file=sys.stderr)

    # X/Twitter-specific searches for key accounts
    x_accounts_batch = " OR ".join(
        [f"site:x.com/{acc}" for acc in AI_NEWS_ACCOUNTS[:12]]
    )
    try:
        x_results = list(ddgs.text(x_accounts_batch, timelimit="d", max_results=12))
        all_results.extend(x_results)
    except Exception as e:
        print(f"  ⚠ X account search skipped: {e}", file=sys.stderr)

    # Deduplicate by URL
    seen: set[str] = set()
    unique: list[dict] = []
    for item in all_results:
        url = item.get("href", "")
        if url not in seen:
            seen.add(url)
            unique.append(item)

    print(f"  ✓ Collected {len(unique)} unique news items")
    return unique[:50]


# ── 2. Synthesise with Claude ─────────────────────────────────────────────────

def generate_summary(news_items: list[dict], date_str: str) -> str:
    """Call the Claude API to produce an HTML executive summary."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    news_text = "\n\n---\n\n".join(
        f"Title: {item.get('title', '(no title)')}\n"
        f"URL:   {item.get('href', '')}\n"
        f"Blurb: {item.get('body', '(no description)')}"
        for item in news_items
    )

    prompt = f"""You are an AI news curator writing a daily executive brief for {date_str}.

The reader is Han Choe — a tech-savvy professional who follows leading AI researchers,
lab CEOs (Anthropic, OpenAI, Google DeepMind, Hugging Face), and AI news curators on X.
He wants signal, not noise: real product launches, important research, geopolitical AI
developments, and sharp takes from frontier AI figures.

Below are {len(news_items)} raw news items fetched from the past 24 hours:

{news_text}

── Instructions ────────────────────────────────────────────────────────────────
1. Identify the 5–8 most significant, genuinely new AI stories.
2. Group them under themed sections using emojis (e.g. "🚀 Model Releases",
   "⚠️ AI Policy & Safety", "🔬 Research", "🌐 Geopolitics & Industry",
   "🛠️ Tools & Developer News"). Use only the sections that apply.
3. For each story write:
   - A concise <h3> headline
   - 2–3 sentence summary (plain <p>) explaining what happened and why it matters
   - A <small class="source"> line with the source/URL (keep it short)
4. Skip anything not directly about AI/ML. Skip vague or duplicate items.
5. Keep each story tight — this is an executive brief, not a blog post.
6. Return ONLY the inner HTML (no <html>, <head>, or <body> tags).
   Use these tags: <h2>, <h3>, <p>, <small class="source">, <hr>.
────────────────────────────────────────────────────────────────────────────────"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


# ── 3. Send Email ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      background: #f4f4f5;
      padding: 24px 16px;
      color: #1a1a1a;
    }}
    .wrapper {{ max-width: 660px; margin: 0 auto; }}
    .header {{
      background: #111;
      color: #fff;
      border-radius: 10px 10px 0 0;
      padding: 28px 32px 24px;
    }}
    .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }}
    .header p  {{ font-size: 13px; color: #aaa; margin-top: 6px; }}
    .body {{
      background: #fff;
      border-radius: 0 0 10px 10px;
      padding: 28px 32px 32px;
    }}
    h2 {{
      font-size: 15px;
      font-weight: 700;
      color: #555;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin: 28px 0 14px;
      padding-bottom: 6px;
      border-bottom: 1px solid #eee;
    }}
    h3 {{
      font-size: 17px;
      font-weight: 700;
      color: #111;
      margin: 20px 0 6px;
      line-height: 1.3;
    }}
    p {{
      font-size: 15px;
      line-height: 1.65;
      color: #444;
      margin-bottom: 6px;
    }}
    small.source {{
      display: block;
      font-size: 12px;
      color: #999;
      margin-top: 4px;
    }}
    hr {{
      border: none;
      border-top: 1px solid #f0f0f0;
      margin: 28px 0;
    }}
    .footer {{
      text-align: center;
      font-size: 12px;
      color: #bbb;
      margin-top: 18px;
      padding-bottom: 8px;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🧠 AI News Executive Summary</h1>
      <p>{date_str} &nbsp;·&nbsp; Curated from your X AI + News list</p>
    </div>
    <div class="body">
      {body}
    </div>
  </div>
  <p class="footer">Generated by Claude · Delivered daily at 7 AM ET</p>
</body>
</html>
"""


def send_email(html_body: str, date_str: str) -> None:
    """Send the formatted email via Gmail SMTP."""
    sender = os.environ["GMAIL_SENDER_EMAIL"]       # han.choe88@gmail.com
    password = os.environ["GMAIL_APP_PASSWORD"]      # Gmail App Password (16 chars)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🧠 Daily AI News Brief — {date_str}"
    msg["From"] = f"AI News Brief <{sender}>"
    msg["To"] = RECIPIENT_EMAIL

    full_html = HTML_TEMPLATE.format(date_str=date_str, body=html_body)
    msg.attach(MIMEText(full_html, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, RECIPIENT_EMAIL, msg.as_string())

    print(f"  ✓ Email sent to {RECIPIENT_EMAIL}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    date_str = datetime.now().strftime("%A, %B %-d, %Y")
    print(f"\n🗞  Daily AI News Brief — {date_str}\n")

    print("🔍 Fetching AI news...")
    news_items = fetch_ai_news()
    if not news_items:
        print("❌ No news items found. Aborting.", file=sys.stderr)
        sys.exit(1)

    print("✍️  Generating summary with Claude...")
    summary_html = generate_summary(news_items, date_str)

    print("📧 Sending email...")
    send_email(summary_html, date_str)

    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()
