---
name: scraping-requests-bs4
description: `httpx` / `requests` + `beautifulsoup4` for static HTML scraping — session reuse, retry discipline, parsing patterns. TRIGGER for simple static pages. SKIP when JS rendering or hosted conveniences are needed.
---

# requests + BeautifulSoup (static scraping)

> **Stub — not yet written.** Flesh out as usage patterns reveal opinions worth capturing.

## When to use

- Target pages are server-rendered HTML; no JS required.
- Small, script-like scrapers where Playwright / Firecrawl would be overkill.

## When NOT to use

- JS-rendered content — see `scraping-playwright.md`.
- Large crawling jobs with rate limiting and markdown conversion — see `scraping-firecrawl.md`.

## Canonical principles

TODO
