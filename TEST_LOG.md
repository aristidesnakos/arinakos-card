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

## 18 Nov 2026 — paid call booking (`/book`, predictions written before testing)

Setup: `booking` in `card.json` points to the existing Cal.com event "Consultation" (30 min, $70 USD, Stripe on),
`https://cal.com/ari-nakos/consultation`. Cal.com stays the booking and payment tool; the site only links out.
The end-to-end test uses a hidden $0 copy of that event that Ari makes, because Cal.com's Stripe app has no
test mode and no live charge is allowed.

| # | Test | Prediction | Result |
|---|---|---|---|
| B1 | `booking: null` build | `public/`, vCard, sitemap and `vercel.json` byte-identical to the last commit; no `/book` | **Pass.** `index.html`, `ari-nakos.vcf`, `sitemap.xml` and `vercel.json` byte-identical to HEAD; no `public/book` |
| B2 | SEO heads, local `/` and `/book` | Both pass: `/book` title ≤ 60, description ≤ 155; `/` unchanged (41 / 143) | `PASS: 2 page(s) measured, 0 failing, 0 warning(s)`: `/` title 41 / description 143; `/book` title 38 / description 133 (after teaching `check_seo_heads.py` to read `book/index.html`) |
| B3 | `/` local | Save contact still the only primary; "Book a paid call" is the last secondary button, links to `/book` | **Pass.** One `.primary` (Save contact, 62 px); "Book a paid call" is the 5th button, 56 px, `href=/book` |
| B4 | `/book` local, CSP enforced | No console errors; no request leaves the origin before the button is tapped (the photo is inline) | **Pass.** Local server sending the `vercel.json` headers: page styled (style hash matches), no console errors, no requests before the injected ones in B5 |
| B5 | CSP blocks third parties on `/book` | An injected `<script src>` / `<img src>` to another host is refused by the CSP | **Pass.** Injected jsDelivr script (`script-src-elem`), `example.com` image (`img-src`) and an inline `<style>` were all refused; script never ran |
| B6 | Lighthouse mobile, local `/book` and `/` | Perf ≥ 95, A11y 100 on both | **Pass.** `/book` Perf 100, A11y 100, BP 100, SEO 100 (LCP 0.9 s, CLS 0, TBT 10 ms); `/` 100 / 100 / 100 / 100 |
| B7 | "Pick a time" button | Opens the Cal.com Consultation page showing 30 min and $70 | **Partial.** Button `href` is `https://cal.com/ari-nakos/consultation` (HTTP 200); Cal.com's public data for that event says 30 min, 7000 cents USD, Stripe enabled. Not yet opened by hand |
| B8 | iOS Simulator: import the new `.vcf` | Contact shows a fourth link labelled "Book a call" → `arinakos.com/book` | **Pass.** Read from the simulator's AddressBook DB (the Contacts view wouldn't scroll, same fault as test 6): new contact has LinkedIn, The Auspicious Company, Card, and **Book a call → https://arinakos.com/book** |
| B9 | Test booking on the hidden $0 copy | Booking confirmed; confirmation email and calendar invite with a video link arrive | **Pass.** Hidden $0 copy `cal.com/ari-nakos/consultation-test` (Stripe off, hidden; real Consultation still $70, Stripe on). Booked Thu 19 Nov 18:00–18:30 Athens as Ari Nakos / ari@theauspiciouscompany.com: "This meeting is scheduled"; confirmation email from hello@cal.com arrived in 20 s; Google Calendar event on ari@theauspiciouscompany.com with Cal Video link `app.cal.com/video/…` and a reschedule/cancel link. Payment step not exercised (no live charge allowed). Found: the real event refunded only if cancelled 2 business days before, but `/book` says 24 hours. Fixed in Cal.com on Ari's call: now "if cancelled 1 calendar day before" (Cal.com has no hours unit); public event data reads `refundDaysCount: 1, refundCountCalendarDays: true`, price and Stripe unchanged. Cleanup: test booking cancelled ("This event is canceled", gone from Google Calendar) and the test event deleted (`/consultation-test` now 404; `/consultation` 200) |
| B10 | SEO heads, live `/` and `/book` after deploy | Both pass, same numbers as B2 | Deployed 18 Nov (commit 1a5294e). `arinakos.com` not registered yet (whois: no match), so measured on `personal-biz-card.vercel.app`: `PASS: 2 page(s) measured, 0 failing, 0 warning(s)` (/ 41 / 143, /book 38 / 133). Re-run on arinakos.com once the domain is live |
| B11 | Live headers after deploy | `/book` has hash-only CSP with no `script-src` host; `.vcf` live with item4 | **Pass** on `personal-biz-card.vercel.app`: `/book` CSP is `default-src 'none'` + one style hash, matching `vercel.json`; live `/book` byte-identical to the local build; `.vcf` has item4 "Book a call"; sitemap lists `/book`. First request after deploy got a 404 while the alias switched; 200 seconds later |

## 18 Nov 2026 — redesign and `/work` portfolio (predictions written before testing)

Design agreed with Ari in the session: `/` stays the scan-to-save card (restyled: display serif for the name, ruled link
list, a "Things I've built" link at the bottom); new `/work` lists personal ventures from `work.json` in three sections
(Japanese, E-commerce, Physical Intelligence), one cropped screenshot (self-hosted WebP) and one line each, taken from each
product's live site or Ari's own wording. `/book` picks up the new style; `/me` is unchanged. One self-hosted font
(Brygada 1918 SemiBold, SIL OFL, Latin subset, 7.2 KB woff2) is inlined as a `data:` URI, so every CSP gains `font-src data:`.
Final look confirmed by Ari after comparing options side by side (fonts Brygada 1918 / Gloock / Schibsted Grotesk / Bricolage Grotesque, four card layouts, three `/work` layouts): he kept option A in each, which is what is built.
Honest note on W2: the build script prints title and description lengths, so those numbers were seen before this table.

| # | Test | Prediction | Result |
|---|---|---|---|
| W1 | Build with `work.json` removed | No `/work` folder, no "Things I've built" link on `/`, no `/work` in sitemap or `vercel.json` || **Pass.** No `public/work`, 0 `/work` links on `/`, 0 sitemap entries, no `/work` header in `vercel.json`. Restored and rebuilt after |
| W2 | SEO heads, local `/`, `/book`, `/work` | PASS: `/` 41 / 143, `/book` 38 / 133, `/work` 42 / 139. Re-measured over HTTP from the local CSP server with the same result (`seo-post-task-check`). Live run waits for the deploy || `PASS: 3 page(s) measured, 0 failing, 0 warning(s)`: `/` 41 / 143, `/book` 38 / 133, `/work` 42 / 139 |
| W3 | `/` at 375×812, light and dark | Save contact is the only filled button and sits above the fold; every link ≥ 48 px tall; no rendered text under 18 px || **Pass, one note.** Save contact bottom edge at 365 px of 812, the only solid button (the "Things I've built" link is a lightly tinted panel). All links on `/` and `/book` ≥ 48 px. On `/work` each product name's own line box is 35 px, but its link covers the whole entry (317–366 px tall; `elementFromPoint` at three points per entry hit the link). Smallest rendered text 18 px on all pages, both schemes |
| W4 | Contrast of every text colour pair, light and dark | All ≥ 4.5:1 (AA); gold is never used for text || **Pass.** Lowest ratio per page, light: `/` 6.61 (muted on the tinted panel), `/book` 7.41, `/work` 7.41. Dark: `/` 8.86, `/book` 9.01, `/work` 10.11. Gold is used for the photo ring, rules, list markers and `aria-hidden` arrows, and in dark mode as the button fill under navy text (9.0:1), as before |
| W5 | CSP enforced (local server sending the `vercel.json` headers) | `/`, `/book`, `/work` render styled with the serif and no console errors; an injected external script, external image and inline style on `/work` are all refused || **Pass.** All three render styled with Brygada (`document.fonts` reports it loaded) and no console errors. On `/work` the injected jsDelivr script (`script-src-elem`), inline `<style>` (`style-src-elem`) and `example.com` image (`img-src`) were refused; the script never ran. Side evidence: after one rebuild the local server still sent the old hash and `/work` rendered unstyled |
| W6 | Network log on `/` and `/work` | No request leaves the origin; `/work` loads its 6 WebP images and nothing else || **Pass.** `/` makes no request after the document. `/work` requests only its own `/work/*.webp` files (lazy-loaded as you scroll); no other host |
| W7 | Lighthouse mobile, local `/`, `/book`, `/work` | Perf ≥ 95, A11y 100, Best Practices 100, SEO 100 on all three || **Pass.** `/`, `/book`, `/work` each Perf 100, A11y 100, BP 100, SEO 100. LCP 1.0 s / 1.0 s / 1.4 s, CLS 0, TBT 0 ms. Re-run on `/` and `/work` after two last CSS fixes on `/work` (section number no longer wraps; ↗ stays with its domain): same 100s |
| W8 | Page weight | `/` ≤ 30 KB (font adds ~10 KB to 13.9 KB); `/work` HTML ≤ 35 KB plus ≤ 100 KB of images || **Pass.** `/` 25.6 KB, `/book` 24.8 KB, `/work` 31.4 KB plus 89.4 KB of images (6 WebP, 12–21 KB each) |
| W9 | Every product link on `/work` | Each returns HTTP 200 and matches `work.json` || **Pass.** All six return 200: michikanji.com, tandash.michikanji.com, llanai.com, kanjifun.com, swimmingrhodes.gr (redirects to its Greek `/el` home), fieldpi.com. Links in `/work` match `work.json` |
| W10 | No horizontal scroll at 320 px and 375 px | `scrollWidth` equals the viewport width on `/`, `/book`, `/work` || **Pass.** `scrollWidth` equals the viewport at 320 px (dark), 375 px (light) and 390 px (emulated phone, both schemes) on all three pages |
| W11 | Unchanged files | `.vcf`, images and `/me` page byte-identical to HEAD; `/me` CSP differs only by `font-src data:` || **Pass.** Only `index.html`, `book/index.html` and `sitemap.xml` changed in `public/`, plus the new `work/`. `.vcf`, images and `/me` are byte-identical to HEAD; scripted compare confirms the `/me` CSP differs only by `font-src data:` |
| W12 | Live after deploy (18 Nov, Ari's yes, commit 79369df) on `personal-biz-card.vercel.app`: SEO heads, page bytes, headers | Same SEO numbers as W2; live pages byte-identical to `public/`; each page's CSP matches `vercel.json` | **Pass.** `PASS: 3 page(s) measured, 0 failing, 0 warning(s)` (41 / 143, 38 / 133, 42 / 139). `/`, `/book`, `/work`, `/me` byte-identical to the local build; CSP on all four matches `vercel.json`; `/work/*.webp` served as `image/webp`; sitemap lists `/`, `/book`, `/work`; `.vcf` still `text/vcard`. `arinakos.com` does not resolve yet, so re-run there once the domain is live |

## 18 Nov 2026 — palette "Stone and Cobalt" (predictions written before testing)

Ari picked palette C from four light/dark pairs. Site tokens change in `src/style.css` (gold accent renamed `--detail`); the share
image (`og.png`) is regenerated in the dark palette with the display face. QR art, Wallet pass and `/me` icons keep navy and gold.

| # | Test | Prediction | Result |
|---|---|---|---|
| C1 | Contrast of every rendered text colour, `/`, `/book`, `/work`, light and dark | All ≥ 4.5:1; lowest is secondary text on the tinted panel, ~6.0:1 light and ~6.9:1 dark || **Pass.** Lowest ratio light: `/` 6.02 (secondary text on the tinted panel), `/book` 6.71, `/work` 6.71. Dark: `/` 6.94, `/book` 7.64, `/work` 7.64. Smallest text 18 px; no horizontal scroll at 320 or 390 px |
| C2 | No old colours left | No `#14213D`, `#C48C28`, `#E0B04F`, `#FAF8F3`, `#0E1628` in the three built pages || **Pass.** 0 matches in all three pages |
| C3 | Unchanged outputs | `.vcf`, favicons, `/me` page and icons, QR files byte-identical to main; only the three pages, `og.png`, `vercel.json` hashes change || **Pass.** `git diff main -- public/` lists only `index.html`, `book/index.html`, `work/index.html` and `og.png` (plus new hashes in `vercel.json`) |
| C4 | CSP enforced locally | Pages render styled with no console errors (new style hashes in `vercel.json`) || **Pass.** All three pages, both modes, at 320 and 390 px: styled background, Brygada loaded, no console errors |
| C5 | Lighthouse mobile, local `/`, `/book`, `/work` | Perf ≥ 95, A11y 100, BP 100, SEO 100 || **Pass on repeat runs.** Runs 1 and 4 were taken with the Unity editor using about two cores (load average 11–14), so CPU-throttled blocking time spiked: `/` once 70 (3.2 s TBT), then 99, 99, 100; `/book` 100, 93, 100, 100; `/work` 100, 75, 100, 100 (`/book` and `/work` contain no script). A11y, BP and SEO were 100 in every run. One late change after the first runs: the button shadow was softened in light and removed in dark |
| C6 | SEO heads, local | PASS, same numbers as W2 (copy unchanged) || `PASS: 3 page(s) measured, 0 failing, 0 warning(s)`: 41 / 143, 38 / 133, 42 / 139, measured over HTTP from the local CSP server |
| C7 | Live after deploy (18 Nov, Ari's yes, commit d7feff9) on `personal-biz-card.vercel.app` | Same SEO numbers; pages and `og.png` byte-identical to `public/`; CSP matches `vercel.json` | **Pass.** `PASS: 3 page(s) measured, 0 failing, 0 warning(s)` (41 / 143, 38 / 133, 42 / 139); `/`, `/book`, `/work`, `/me` and `og.png` byte-identical; CSP on all four pages matches. Link-preview caches (iMessage, LinkedIn, WhatsApp) may show the old navy image until they refresh. `arinakos.com` still unregistered |
