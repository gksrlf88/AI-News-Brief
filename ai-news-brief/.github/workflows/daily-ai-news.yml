name: Daily AI News Brief

on:
  schedule:
    # 7:00 AM ET (UTC-5 standard / UTC-4 daylight)
    # Using 12:00 UTC to hit ~7 AM ET in winter; shifts to 8 AM ET during DST
    # To lock to exactly 7 AM ET year-round, a Lambda/Cloud Scheduler is needed.
    - cron: '0 12 * * *'
  # Allow manual trigger from the Actions tab
  workflow_dispatch:

jobs:
  send-ai-news-brief:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run AI News Brief
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_SENDER_EMAIL: ${{ secrets.GMAIL_SENDER_EMAIL }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
        run: python scripts/ai_news_brief.py
