# 🧠 Daily AI News Brief

A GitHub Actions workflow that fetches the latest AI news, synthesizes an executive summary using Claude, and emails it to you every morning at 7 AM ET.

---

## How It Works

1. **Fetches** recent AI news via DuckDuckGo (no API key needed) using targeted queries matching your X "AI + News" list accounts
2. **Synthesizes** the top 5–8 stories into a structured HTML email using Claude (`claude-sonnet-4-5`)
3. **Emails** the brief to `han.choe88@gmail.com` via Gmail SMTP

---

## One-Time Setup

### Step 1 — Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it something like `ai-news-brief`
3. Set it to **Private**
4. Click **Create repository**

### Step 2 — Upload these files

Upload the entire folder contents to your new repo. The structure should look like this:

```
ai-news-brief/
├── .github/
│   └── workflows/
│       └── daily-ai-news.yml
├── scripts/
│   └── ai_news_brief.py
├── requirements.txt
└── README.md
```

You can drag-and-drop the files at `github.com/<your-username>/ai-news-brief` or use the GitHub CLI / desktop app.

### Step 3 — Get a Gmail App Password

Gmail requires an App Password (not your regular password) for SMTP access.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Make sure **2-Step Verification** is enabled
3. Search for "App passwords" in the search bar at the top
4. Click **App passwords**
5. Under "App name", type `AI News Brief` → click **Create**
6. Copy the 16-character password shown (you won't see it again)

### Step 4 — Add GitHub Secrets

In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add these three secrets:

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (from [console.anthropic.com](https://console.anthropic.com)) |
| `GMAIL_SENDER_EMAIL` | `han.choe88@gmail.com` |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from Step 3 |

### Step 5 — Enable Actions

If GitHub Actions isn't already enabled for your repo, go to the **Actions** tab in your repo and click **"I understand my workflows, go ahead and enable them"**.

---

## Running Manually

To send a brief right now (without waiting for 7 AM), go to:

**Actions tab → Daily AI News Brief → Run workflow → Run workflow**

---

## Schedule & Timezone

The workflow runs at `0 12 * * *` (UTC), which is:
- **7:00 AM ET** during Eastern Standard Time (Nov–Mar)
- **8:00 AM ET** during Eastern Daylight Time (Mar–Nov)

GitHub Actions cron runs in UTC only. If you want to lock it to exactly 7:00 AM ET year-round, you'd need to update the cron to `0 11 * * *` during DST months, or migrate to AWS EventBridge / Google Cloud Scheduler which support timezone-aware scheduling.

---

## Customization

- **Change recipient**: Edit `RECIPIENT_EMAIL` in `scripts/ai_news_brief.py`
- **Add/remove news queries**: Edit the `queries` list in `fetch_ai_news()`
- **Change the model**: Edit the `model=` parameter in `generate_summary()`
- **Adjust number of stories**: Change the `5–8` in the prompt inside `generate_summary()`
