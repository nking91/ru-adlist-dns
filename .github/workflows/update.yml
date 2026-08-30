name: Update RU AdList DNS

on:
  schedule:
    - cron: "0 3 * * *"  # каждый день в 03:00 UTC (06:00 МСК)
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Generate list
        run: python generate.py

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add ru-adlist-dns.txt
          git diff --staged --quiet || git commit -m "Update RU AdList DNS"
          git push
