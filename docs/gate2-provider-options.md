# Gate 2 Provider Options

Status: planning only. No provider is approved for implementation yet.

Last reviewed: 2026-08-28 KST.

This document compares provider candidates for Gate 2 investment and general research. Free API lists or third-party summaries may be used only to discover candidates. Pricing, free quota, rate limits, license, and data handling must be checked against each provider's official documentation before implementation.

No API keys were created, no live API calls were made, no accounts were connected, and no secrets were stored while preparing this document.

## Local Candidate Material Checked

The current AIOffice workspace contains no separate free-API catalog. The only local provider references found are preserved in `AI_Office_requirements_review_v0.23.md`, including:

- Korea Investment Securities KIS Open API as an official read-only brokerage candidate.
- Toss Securities Open API as an official read-only brokerage candidate.
- Kakao Pay Securities remains capture-input based until an official personal account API is verified.
- OpenDART, Cloudflare, Supabase, OpenAI, and Instagram references from earlier Gate planning.

## Gate 2 Capability Map

| Capability | Need | Existing AIOffice coverage | New provider need |
| --- | --- | --- | --- |
| Web and latest news search | Discover recent sources, current events, and source URLs | ChatGPT/Codex can assist during manual planning, but no production Core provider is approved | Yes, if automated research is approved |
| Official economic indicators | Rates, inflation, FX, GDP, macro releases | None connected | Yes |
| Korean and US stock/ETF market data | Prices, candles, volume, market metadata, ETF data | None connected | Yes |
| Brokerage account lookup | Read-only holdings and balances | None connected; approved boundary is read-only only | Yes, after user approval |
| Disclosure and official company filings | Korean disclosures and company facts | None connected | Yes for Korean issuers |
| Document extraction and JSON structuring | Convert docs, filings, pages, and screenshots into report JSON | Existing module result format is Markdown + JSON only | Possibly OpenAI API or local parsers after approval |
| Source-grounded summarization and cross-checking | Claims, evidence, conflicts, uncertainty | Planned module contract only | Possibly OpenAI API after approval |
| Translation | Korean/English source handling | Existing models can translate during manual work | Possibly existing AI capability; no separate translation provider recommended yet |

## Provider Comparison

| Provider | Capability | Official basis | Price | Free quota | Limits | Quality | License | Personal data | Stability | Auth env names | Existing duplicate | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Brave Search API | Web, news, image, and LLM-context search discovery | Official pricing/API page, checked 2026-08-28: https://brave.com/search/api/ | Search: $5 per 1,000 requests; Answers: $4 per 1,000 requests plus token pricing | $5 monthly credits per plan, credit card may be required | Search plan shows 50 QPS; Answers default 2 RPS in docs | Independent web index, news and web results, useful for discovery | Redistribution and attribution terms must be reviewed before production | Sends search queries; avoid personal, account, or portfolio data | Public API with published plans; pricing can change | `BRAVE_SEARCH_API_KEY` | Overlaps with manual ChatGPT/Codex web search, but not with automated production Core | Recommended for automated web/news discovery if user approves account, attribution, and query privacy controls |
| Tavily API | AI-oriented web search, extract, crawl, and research | Official docs/pricing, checked 2026-08-28: https://docs.tavily.com/documentation/api-credits and https://www.tavily.com/pricing | Pay-as-you-go $0.008 per credit; paid monthly plans start at $30 | 1,000 credits/month, no credit card required | Request cost varies by search depth and tool; exact rate limits depend on plan | Strong fit for agentic search and extraction | Terms and redistribution limits must be reviewed before production | Sends queries and URLs; avoid personal, account, or portfolio data | Public API, credit model may affect predictability | `TAVILY_API_KEY` | Overlaps with Brave and OpenAI web search | Recommended as a lower-friction search/extract candidate; choose only one primary web-search provider initially |
| NewsAPI | News search and headlines | Official pricing page, checked 2026-08-28: https://newsapi.org/pricing | Business plan starts at $449/month; Advanced $1,749/month | Developer plan is $0 for development/testing only | Developer: 100 requests/day, 24-hour article delay, development-only | Useful news discovery; not full article content | Developer plan is not for production or internal staging; full content unavailable | Sends queries; avoid sensitive subjects that reveal portfolio or account details | Mature service, but free tier unsuitable for production | `NEWSAPI_KEY` | Duplicates Brave/Tavily news discovery | Hold. Development-only free tier and high production price do not fit initial budget |
| FRED API | US official economic indicators | Official FRED API docs and terms, checked 2026-08-28: https://fred.stlouisfed.org/docs/api/fred/v2/ and https://fred.stlouisfed.org/docs/api/terms_of_use.html | 확인 불가 from official pricing page; API key required | 확인 불가 | Official docs mention 429 rate limiting but not a fixed public quota in the checked pages | Strong official US macro source with JSON/XML endpoints | Third-party series may have copyright restrictions; app must display required FRED notice | API key registration data; queries normally non-personal | Official Federal Reserve Bank of St. Louis service; terms may change | `FRED_API_KEY` | No duplicate official US macro source | Recommended for US macro indicators after approval |
| Bank of Korea ECOS | Korean official economic indicators | Official ECOS API entry point and BOK public explanation, checked 2026-08-28: https://ecos.bok.or.kr/api/ and https://www.bok.or.kr/portal/bbs/B0000522/view.do?menuNo=201692&nttId=10070977 | 확인 불가 | 확인 불가 | 확인 불가 in official pages checked | Official Korean macro, rates, FX, and economic statistics source | Terms must be reviewed during account/key request | API key registration data; queries normally non-personal | Official Bank of Korea system | `ECOS_API_KEY` | No duplicate official Korean macro source | Recommended for Korean macro indicators after official key/rate terms are approved |
| OpenDART | Korean company filings and disclosures | Official OpenDART introduction and API guide, checked 2026-08-28: https://opendart.fss.or.kr/intro/main.do and https://engopendart.fss.or.kr/guide/detail.do?apiGrpCd=DE006&apiId=AE00079 | 확인 불가 | Usually public OpenAPI key based; exact free quota must be confirmed from account page | Official guide lists call-limit-exceeded status and notes at least 20,000 requests in common cases, but thresholds may differ | Official Korean filings and structured disclosure data | Terms require compliance with OpenDART rules | API key registration data; disclosure data is public | Official Financial Supervisory Service system | `OPENDART_API_KEY` | No duplicate official Korean disclosure source | Recommended for Korean issuer filings after approval |
| Korea Investment Securities KIS Open API | Korean/overseas stock, ETF, balance, and market data candidate | Official KIS Developers docs, checked 2026-08-28: https://apiportal.koreainvestment.com/docs and https://apiportal.koreainvestment.com/apiservice-summary | 확인 불가 | 확인 불가 | Rate limits and account-specific support must be verified with issued app/account; portal posts limit notices | Official brokerage and market data for user account scope | Brokerage terms and market-data redistribution rules must be reviewed | Sensitive account and holdings data if account APIs are used | Official brokerage API, notices can change limits | `KIS_APP_KEY`, `KIS_APP_SECRET`, `KIS_ACCESS_TOKEN` | Required by requirements for read-only brokerage candidate | Recommended only for read-only lookup after user approval; exclude all order scopes |
| Toss Securities Open API | Korean/US market data and read-only account asset lookup candidate | Official Toss Securities docs, checked 2026-08-28: https://developers.tossinvest.com/docs | 확인 불가 from docs checked | 확인 불가 | Published TPS groups: ACCOUNT 1 TPS, ASSET 5 TPS, STOCK 5 TPS, MARKET_DATA 15 TPS, chart 20 TPS; 429 includes rate-limit headers | Official market data, account list, holdings, exchange rates, calendars, and warnings | Brokerage and market-data redistribution rules must be reviewed | Sensitive account and holdings data for account endpoints | Official docs show versioned API and rate-limit guidance | `TOSSINVEST_CLIENT_ID`, `TOSSINVEST_CLIENT_SECRET`, `TOSSINVEST_ACCESS_TOKEN`, `TOSSINVEST_ACCOUNT_ID` | Required by requirements for read-only brokerage candidate | Recommended only for read-only lookup after user approval; exclude order and conditional-order scopes |
| Kakao Pay Securities | Account and holdings data | Local requirement notes no verified official personal account API; KakaoPay developer/forum reference from v0.22 | 확인 불가 | 확인 불가 | 확인 불가 | No verified official personal account API found in project basis | 확인 불가 | Would involve sensitive account data if ever connected | 확인 불가 | Not defined until official API is verified | Capture-input flow already covers first version | Exclude as API provider for now; keep capture input until official personal account API is verified |
| Alpha Vantage | Global market data and some indicators | Official support/pricing pages, checked 2026-08-28: https://www.alphavantage.co/support/ and https://www.alphavantage.co/premium/ | Free for many endpoints; premium available for higher volume and realtime/delayed regulated data | 25 API requests/day; higher for verified open-source or educational projects | Standard free limit 25/day; realtime and 15-minute delayed US market data are premium-only | Broad structured market data; free quota too low for frequent scheduled reports | Market data licensing and realtime restrictions require review | Sends tickers and queries; no account data needed | Established public API; free quota changed from older common assumptions | `ALPHAVANTAGE_API_KEY` | Duplicates KIS/Toss market data for many needs | Hold as fallback for non-account market fixtures; free quota too low for primary scheduled reports |
| OpenAI API | Document extraction, JSON structuring, source-grounded summarization, cross-check reasoning, translation | Official model, structured output, pricing, and data control docs, checked 2026-08-28: https://developers.openai.com/api/docs/models/compare, https://openai.com/index/introducing-structured-outputs-in-the-api/, https://platform.openai.com/docs/models/default-usage-policies-by-endpoint | GPT-5.6 Luna: $0.20 input / $1.20 output per 1M tokens; Terra: $2 input / $12 output per 1M tokens; Web Search billed separately where used | No general free API quota confirmed in checked docs | Rate limits depend on usage tier and model; free tier often unsupported for newest models | Strong structured output and multilingual reasoning; must be source-grounded by design | Output and input usage follows OpenAI API terms; web sources may have their own rights | API data is not used for training by default unless opted in; default abuse monitoring up to 30 days; avoid personal/account data unless approved | Official current model family and structured outputs | `OPENAI_API_KEY` | Duplicates manual ChatGPT/Codex reasoning but not automated module API | Recommended for JSON structuring and cross-check reasoning only after budget, retention, and data-scope approval |

## Existing Capability Without New Providers

- Manual planning, code review, and document drafting through Codex.
- Markdown and JSON result submission through the existing Core/Modules contract.
- Local fixture and mock validation without live provider calls.
- Translation during manual review, where no production API is connected.

## Capability Requiring New Providers

- Automated web/news discovery.
- Official US macroeconomic time series.
- Official Korean macroeconomic time series.
- Korean issuer filings and disclosure extraction.
- Read-only brokerage holdings and balances.
- Automated source-grounded JSON structuring and report synthesis, if not handled manually.

## Recommended Initial Provider Set

Subject to user approval:

- Brave Search API or Tavily API, not both initially, for web/news discovery.
- FRED API for US macro indicators.
- Bank of Korea ECOS for Korean macro indicators.
- OpenDART for Korean disclosures.
- KIS Open API and Toss Securities Open API for read-only account and market-data checks only.
- OpenAI API for structured extraction, source-grounded synthesis, and translation only if data retention and budget controls are approved.

## Hold Or Exclude

- NewsAPI: hold because the free Developer plan is development/testing only and production pricing is high for the current budget.
- Alpha Vantage: hold because 25 requests/day is too low for the planned scheduled research cadence and realtime/delayed US market data is premium-only.
- Kakao Pay Securities API: exclude until an official personal account/holdings API is verified; continue capture input.
- Any order-capable brokerage scope: exclude from Gate 2.

## Environment Variable Names

Names only; do not create or populate these values before approval.

- `BRAVE_SEARCH_API_KEY`
- `TAVILY_API_KEY`
- `NEWSAPI_KEY`
- `FRED_API_KEY`
- `ECOS_API_KEY`
- `OPENDART_API_KEY`
- `KIS_APP_KEY`
- `KIS_APP_SECRET`
- `KIS_ACCESS_TOKEN`
- `TOSSINVEST_CLIENT_ID`
- `TOSSINVEST_CLIENT_SECRET`
- `TOSSINVEST_ACCESS_TOKEN`
- `TOSSINVEST_ACCOUNT_ID`
- `ALPHAVANTAGE_API_KEY`
- `OPENAI_API_KEY`

## Expected Free Allowance

- Brave Search API: $5 monthly credits per plan.
- Tavily: 1,000 credits/month.
- NewsAPI: 100 requests/day for development and testing only.
- FRED: 확인 불가.
- ECOS: 확인 불가.
- OpenDART: 확인 불가 from account-independent official docs; API guide shows call-limit errors.
- KIS: 확인 불가.
- Toss Securities: 확인 불가.
- Alpha Vantage: 25 requests/day.
- OpenAI API: 확인 불가 for general free quota.

## Paid Conversion Risk

- Brave, Tavily, OpenAI, NewsAPI, and Alpha Vantage can generate pay-per-use or subscription costs.
- KIS and Toss may require brokerage account setup, IP allowlists, and credential handling even if direct API price is not visible.
- Supabase and Cloudflare remain unconnected in this planning PR and must not be upgraded or deployed here.

## Data Transfer And Security Risks

- Search providers receive query text and may infer user interests. Queries must avoid personal account and portfolio details unless approved.
- Brokerage providers would receive account-scoped requests and return sensitive financial data. These flows require explicit read-only scopes, secret stores, redaction, and retention policies.
- AI providers may receive source text or document excerpts. Personal data, account data, portfolio data, and secrets must be removed unless the user approves a specific data path.
- Market data and news may have redistribution limits. AIOffice reports must preserve source attribution and avoid republishing restricted raw feeds.
- Provider `429`, quota exhaustion, and stale data must be represented in Core state rather than silently retried forever.

## User Approval Required Before Implementation

- Which web/news provider to use first: Brave or Tavily.
- Whether to include OpenAI API in automated Gate 2 flows, and which model tier is allowed.
- Whether FRED, ECOS, and OpenDART API keys may be requested.
- Whether KIS and Toss read-only account access may be configured.
- Exact secret store for each environment variable.
- Whether raw provider payloads may be stored, and for how long.
- Monthly spend ceiling per provider.
- Whether any provider with unclear official free quota may be used.
