# Test log — arinakos.com card

Each test has a prediction and a result. Honest note: for the tests on 18 Nov 2026, the predictions were
written into this log after the runs (they were stated in the build plan beforehand). Every test from
"Ari's real-phone tests" on has its prediction written here before it runs.

## 18 Nov 2026 — automated checks (Claude)

| # | Test | Prediction | Result |
|---|---|---|---|
| 1 | Lighthouse mobile, live `personal-biz-card.vercel.app` | Accessibility 100, Performance ≥ 95 | **Perf 99, A11y 100, Best Practices 100, SEO 100.** LCP 1.0 s, CLS 0, TBT 100 ms |
| 2 | Page weight | < 60 KB | **index.html 13.9 KB** (photo inlined, no other requests); vCard 20.6 KB |
| 3 | Headers on live deploy | CSP with hashes only, correct vCard type | **Pass.** `/` and `/me` have hash-only CSP; `.vcf` is `text/vcard; charset=utf-8`, `inline; filename="ari-nakos.vcf"`; `nosniff`, `no-referrer`, HSTS |
| 4 | Secrets not deployed | `/certs/*` and source files are 404 | **Pass.** `.vercelignore` only uploads `public/` and `vercel.json`; `/certs/pass.key` and `/build.py` are 404 |
| 5 | iOS 26.5 Simulator, Safari: page | Renders like the desktop preview | **Pass.** Same layout, photo ring and type as designed |
| 6 | iOS Simulator, Safari: tap Save contact | Contact preview sheet with photo | **Inconclusive.** The sheet opened but rendered blank, and the simulator's home-screen icons were blank too, so this is a simulator rendering fault. Re-check on a real iPhone (test R3) |
| 7 | iOS vCard parser: import the live `.vcf` into the simulator's Contacts | All fields and the photo parsed | **Pass.** First/last name, org, title, work email, URLs labelled LinkedIn / The Auspicious Company / Card, LinkedIn social profile (service `linkedin`, user `aristidesnakos`), thumbnail and full-size photo. Screenshot: `test-evidence/ios-sim-contact.png` |
| 8 | SEO heads (title ≤ 60, description ≤ 155), local `public/` | Pass | `PASS: 1 page(s) measured, 0 failing, 0 warning(s)` (title 41, description 143) |
| 9 | SEO heads, live preview URL | Pass | `PASS: 1 page(s) measured, 0 failing, 0 warning(s)` |
| 10 | JavaScript off | Page and Save contact work | **Pass by construction.** JS only reveals the in-app-browser hint; Save contact is a plain link to the static `.vcf` |

**Dropped:** the JS "Met on <date>" note. It could only be verified through the Safari contact sheet, which the
simulator can't render, so per the cut order it isn't shipped.

## QR decode tests

Full detail is in `qr_results.md` (QR session; its predictions were written before each run). Summary:

| File | Prediction | Result (zxing / zbar / OpenCV, 27 conditions) |
|---|---|---|
| `make_qr.py` style A, uppercase URL | 27/27 | **27/27** |
| `qr-a.png`, `qr-a.svg` (rasterised), `qr-a-screen.png` | 27/27 | **27/27 each** |
| Both A wallpapers | 27/27 | First run **26/27 and 23/27**: OpenCV lost the rounded finders in the tall frame. After switching to square finder corners: **27/27 each** |
| Style B files | ~18/27 | 17–18/27 (OpenCV 0/9); B wallpapers 12/27 (zbar misses once scaled down) |

Style A is version 2 (25×25 modules) with `HTTPS://ARINAKOS.COM`. The lowercase fallback is version 3, also 27/27.
On decoders alone, the card is style A. The real-phone tests below decide on B.

## Ari's real-phone tests (predictions written before testing)

Setup: QR on your phone screen at full brightness, the other phone at arm's length (~50 cm). Do each in normal light and in dim light.

| # | Test | Prediction | Result |
|---|---|---|---|
| R1 | iPhone Camera scans style A (`/me` and lock-screen wallpaper) | First try, < 1 s, both lights | |
| R2 | Android Camera + Google Lens scan style A | First try, both lights | |
| R1b/R2b | Same with style B | iPhone first try; may miss on some Android cameras | |
| R3 | iPhone Safari: Save contact | "Create New Contact" sheet with photo, title, company, email, 3 links, LinkedIn row | |
| R4 | Android Chrome: Save contact | Downloads, opens in Contacts with photo and fields | |
| R5 | Uppercase URL opens correctly on both phones | Opens `https://arinakos.com/` | |
| R6 | Wallet pass adds and its QR scans | Adds on first tap; scans first try | |

Rule: keep style B only if it scans first try on every device. Otherwise style A is the card.
