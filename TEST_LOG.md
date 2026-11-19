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
| R1 | iPhone Camera scans style A (`/me` and lock-screen wallpaper) | First try, < 1 s, both lights || **Pass.** Only `public/work/index.html` changed (`vercel.json` untouched, same CSS hash). At 375 and 1280, light and dark: no horizontal scroll, smallest text 18 px, no link under 48 px, lowest contrast 6.71:1 light, 7.64:1 dark; no console errors |
| R2 | Android Camera + Google Lens scan style A | First try, both lights || **Pass.** `PASS: 5 page(s) measured, 0 failing, 0 warning(s)` (`/work` 51 / 152); prodoozie.com 200, no redirect |
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

## 19 Nov 2026 — arinakos.com registered and connected (predictions written before testing)

Setup: fresh `get_purchase_quote` read $12.03 USD for 1 year with auto-renew on, the same as the 18 Nov quote Ari said yes to,
so the earlier yes stood (Ari's rule for this run). Bought with `buy_domain` (order `01M7SAQ5ZNWKYMYYM98SHV3Z84`, status
`completed`), registrant details typed by Ari in the session. Added to project `personal-biz-card` (`prj_wAdfcTV34CU9LgEFmM34GO9bgQn3`):
`arinakos.com` (production) and `www.arinakos.com` → 308 to `arinakos.com`; both verified at once. No other domain or project setting
changed. The plugin Vercel connector bought the domain but returned 404 for the project; the claude.ai Vercel connector saw it and
added the domains.

| # | Test | Prediction | Result |
|---|---|---|---|
| D1 | `python3 check_seo_heads.py https://arinakos.com / /book /work` | `PASS: 3 page(s) measured, 0 failing, 0 warning(s)`, same numbers as W2/C6: 41 / 143, 38 / 133, 42 / 139 | `PASS: 3 page(s) measured, 0 failing, 0 warning(s)`: `/` 41 / 143, `/book` 38 / 133, `/work` 42 / 139 |
| D2 | CSP header on `/`, `/book`, `/work`, `/me` | Each equals its `vercel.json` value character for character | **Pass.** `/`, `/book`, `/work`, `/me` all 200; each CSP equals its `vercel.json` value (scripted string compare) |
| D3 | Live bytes vs `public/` | `/`, `/book`, `/work`, `/me`, `og.png`, `.vcf`, `sitemap.xml`, `robots.txt` byte-identical | **Pass.** All eight byte-identical: `/` 26,180 B, `/book` 25,429, `/work` 32,121, `/me` 2,888, `og.png` 160,272, `.vcf` 21,168 (`text/vcard`), `sitemap.xml` 246, `robots.txt` 66. DNS was live at once: NS `ns1/ns2.vercel-dns.com`, apex and www resolve to Vercel |
| D4 | HTTPS | Valid certificate covering `arinakos.com` (issued by Vercel within minutes); `http://` answers 308 to `https://`; HSTS header present as in `vercel.json` | **Pass.** Let's Encrypt (YR1) certificate, CN and SAN `arinakos.com`, valid 19 Nov 2026 → 17 Feb 2027, verifies in Python and curl; `www` has its own valid certificate. `http://arinakos.com/book` → 308 `https://arinakos.com/book`; HSTS `max-age=63072000; includeSubDomains; preload` on the apex |
| D5 | `https://ARINAKOS.COM` (the printed QR's URL) | 200 with the card, same bytes as `/` (host names are case-insensitive) | **Pass.** `https://ARINAKOS.COM` and `https://ARINAKOS.COM/` → 200, same bytes as `public/index.html`; curl sent `Host: ARINAKOS.COM` and the certificate still verified |
| D6 | `https://www.arinakos.com/book` | 308 to `https://arinakos.com/book` | **Pass.** `https://www.arinakos.com/book` → 308 `https://arinakos.com/book`; `https://www.arinakos.com/` → 308 `https://arinakos.com/`; `http://www.arinakos.com/work` → 308 to `https://www.…/work`, then to the apex (two hops) |
| D7 | Public registration record (RDAP) | Registrar is Vercel's; registrant name, street, phone and email redacted; at most state (ID) and country (US) shown | **Pass, better than predicted.** Registry RDAP: registered 19 Nov 2026 07:18 UTC, expires 19 Nov 2027, registrar Name.com, Inc. (Vercel's registrar), status `client transfer prohibited`. Registrar RDAP shows no registrant data at all: name "Redacted For Privacy", organisation, address and phone of the privacy service Domain Protection Services, Inc. (Denver, CO), contact via Name.com's web form; Ari's state and country are not shown either. Contact verification could not be read yet: `get_domain_contact_verification` returned 400 within 30 minutes of purchase (documented `bought_too_recently`) |
| D8 | `personal-biz-card.vercel.app` | Still 200 with the same bytes | **Pass.** `personal-biz-card.vercel.app/` 200, byte-identical to `public/index.html` |

## 19 Nov 2026 — `/contact` page (predictions written before testing)

Ari's pick: the card moves to `/contact`, centred, with a "Show QR code" button (QR on request). The QR is generated
in the build (segno, error correction H) for `HTTPS://ARINAKOS.COM/CONTACT` and inlined as SVG; the sheet opens with
CSS `:target`, so no script. `/CONTACT` is rewritten to `/contact` in `vercel.json` (paths are case-sensitive) with
the same CSP. `/` is unchanged until the timeline homepage is built. Honest note on K6: the build prints the lengths.

| # | Test | Prediction | Result |
|---|---|---|---|
| K1 | `/contact` at 375×812, light and dark | Photo, name and headline centred; Save contact the only solid button and above the fold; links ≥ 48 px; text ≥ 18 px; contrast ≥ 4.5:1 || **Pass.** Photo, name, headline and QR button centred to the pixel (offset 0); Save contact is the only solid link, bottom edge at 372 of 812; no link under 48 px; smallest text 18 px; lowest contrast 6.71:1 light, 7.64:1 dark; no horizontal scroll |
| K2 | "Show QR code", JS off too | Opens a white full-screen sheet with the QR; "Close" returns to the card; works with JavaScript disabled || **Pass.** With JS on and off: the button sets `#qr`, the sheet shows (`display: grid`, QR 323 px wide at 375); Close sets `#top` and the sheet hides |
| K3 | Decode the QR from a screenshot of the sheet (zxing, zbar, OpenCV) | All three read `HTTPS://ARINAKOS.COM/CONTACT` || **Failed first, then pass.** First build: no decoder read it. The site's shared icon style (`svg{stroke-width:1.9;stroke-linecap:round}`) fattened segno's stroked modules into blobs. Fixed by drawing the QR as filled squares. Then zxing, zbar and OpenCV all read `HTTPS://ARINAKOS.COM/CONTACT` at full, half and quarter size |
| K4 | CSP enforced locally | Styled, no console errors; `/CONTACT` gets the same CSP as `/contact` || **Pass.** No console errors in either mode; local server sends the same CSP for `/CONTACT` and `/contact` (live rewrite to be checked after deploy) |
| K5 | Lighthouse mobile, local `/contact` | Perf ≥ 95, A11y 100, BP 100, SEO 100 || **Pass.** Two runs: Perf 100, A11y 100, BP 100, SEO 100 both times (LCP 1.0 s, CLS 0.001, TBT 0–10 ms) |
| K6 | SEO heads, local | PASS; `/contact` title 38, description 154; others unchanged || `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`: `/contact` and `/CONTACT` 38 / 154; `/`, `/book`, `/work` unchanged |
| K7 | Unchanged outputs | `/`, `/book`, `/work`, `/me`, `.vcf` byte-identical to main || **Pass.** `git diff main -- public/` shows only `sitemap.xml` (adds `/contact`) plus the new `public/contact/`. `/contact/index.html` is 34.7 KB (the inline QR adds about 9 KB) |

## 19 Nov 2026 — timeline homepage at `/` (predictions written before testing)

Ari's pick: timeline A (a line). `/` becomes the homepage: photo, name and headline with a "Contact card" link, his
nine moments (`timeline.json`, his words lightly tidied) on a vertical line with a dot each, then the projects from
`work.json` as a bulleted list. `/work` stays as the version with screenshots. `/` no longer has a script, so its
CSP drops `script-src`. The printed QR art, wallpapers, `/me` QR and the Wallet pass barcode now encode
`HTTPS://ARINAKOS.COM/CONTACT` (`card.json` `qr_url`); the vCard "Card" link points at `/contact`.

| # | Test | Prediction | Result |
|---|---|---|---|
| T1 | `/` at 375×812 and 1280×800, light and dark | Line and dots line up with the years; no horizontal scroll; text ≥ 18 px; links ≥ 48 px tall; contrast ≥ 4.5:1 || **Pass.** At 375 and 1280, light and dark: every dot sits on the line (offset 0) and level with its year; no horizontal scroll; smallest text 18 px; no link under 48 px; lowest contrast 6.71:1 light, 7.64:1 dark. Page height 2582 px at 375 |
| T2 | CSP enforced locally | Styled, no console errors; `/` header has no `script-src` || **Pass.** No console errors on `/`, `/contact`, `/CONTACT`, `/work`, `/book`, `/me`; the `/` CSP is `style-src` hash only, no `script-src` |
| T3 | Lighthouse mobile, local `/` | Perf ≥ 95, A11y 100, BP 100, SEO 100 || **Pass.** Two runs: Perf 100, A11y 100, BP 100, SEO 100 both times (LCP 1.0 s, CLS 0, TBT 0 ms) |
| T4 | SEO heads, local | PASS; `/` title 41, description 140; `/contact`, `/book`, `/work` unchanged || `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`: `/` 41 / 140; `/book` 38 / 133, `/work` 42 / 139, `/contact` and `/CONTACT` 38 / 154 unchanged |
| T5 | QR art decode (`qr_build.py --test`) | Style A files and wallpapers read `HTTPS://ARINAKOS.COM/CONTACT` (version 3) in 27/27 conditions; style B lower, as before || **Pass.** Style A: version 3 (29×29). `qr-a.png`, `qr-a-screen.png`, `qr-a.svg` (rsvg) and both wallpapers 27/27 each. Style B (version 6): 18/27 files, 12/27 wallpapers, same pattern as before |
| T6 | `/contact` sheet QR and `/me` QR | Both decode to `HTTPS://ARINAKOS.COM/CONTACT` || **Pass.** zxing, zbar and OpenCV all read `HTTPS://ARINAKOS.COM/CONTACT` from the `/contact` sheet SVG and `/me`'s `qr-a` art. vCard `item3.URL` is `https://arinakos.com/contact` |
| T7 | Links on `/` | Every outbound link returns 200 with no redirect; internal links resolve on the local server || **Pass, with two known exceptions.** All other outbound links 200, no redirect. LinkedIn answers 999 to scripts (its bot block, as before); swimmingrhodes.gr redirects to its `/el` language page (unchanged link from `work.json`). `/`, `/contact`, `/CONTACT`, `/work`, `/book` all 200 locally |

### Live checks after deploying `/contact` and the timeline homepage (19 Nov 2026)

Deployment `personal-biz-card-oegm7qvd2`, aliased to arinakos.com and www.arinakos.com.

| Check | Result |
|---|---|
| `/`, `/contact`, `/CONTACT`, `/work`, `/book`, `/me`, `.vcf`, QR PNG | All 200 with the right content types; `/CONTACT` rewrite works live |
| CSP and HTML | Every page's live CSP equals `vercel.json`, and the live HTML is byte-identical to the tested build |
| Live QR art | `qr-a.png` and the iPhone wallpaper decode to `HTTPS://ARINAKOS.COM/CONTACT`; live vCard Card link is `/contact` |
| SEO heads, live | `PASS: 5 page(s) measured, 0 failing, 0 warning(s)` (`/` 41 / 140) |

## 19 Nov 2026 — HVAC years 2013–2015 (prediction written before testing)

Ari: the HVAC job ran through 2015. `timeline.json` changes "2013" to "2013–2015"; nothing else on `/` moves.

| # | Test | Prediction | Result |
|---|---|---|---|
| H1 | Rebuild and diff `public/` | Only `public/index.html` (the year and the new style hash in `vercel.json`) changes; title 41 / description 140; SEO heads PASS; CSP still matches | **Pass.** Only `public/index.html` changed (one line); `vercel.json` unchanged because the CSS, and so its hash, didn't change. Title 41 / description 140; `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`. "2013–2015" is the same length as the other ranges, so the layout is unchanged |

Live after deploy `personal-biz-card-eu0liulzm` (arinakos.com): `/` returns 200, CSP matches `vercel.json`, HTML
byte-identical to the build and shows "2013–2015"; live SEO heads `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`.

## 19 Nov 2026 — leaner homepage (predictions written before testing)

Ari: make it more minimal. A moment with a site now links its title (the separate domain line is gone), and the
bulleted "Things I've built" list and "The same, with screenshots" link are replaced by a "Products" link in the
footer row (Products, Contact card, Book a paid call, LinkedIn) that opens `/work`. The description now names the
moments instead of the side projects; `/contact`'s link reads "Timeline and products".

| # | Test | Prediction | Result |
|---|---|---|---|
| L1 | `/` at 375×812 and 1280×800, light and dark | Dots still level with the years; linked titles ≥ 48 px tall; no horizontal scroll; text ≥ 18 px; contrast ≥ 4.5:1; page about 1,000 px shorter on a phone || **Pass.** At 375 and 1280, light and dark: every dot on the line and level with its year; no link under 48 px (linked titles included); no horizontal scroll; smallest text 18 px; lowest contrast 6.71:1 light, 7.64:1 dark. Phone page height 2582 → 1538 px |
| L2 | CSP enforced locally | Styled, no console errors (new style hash written to `vercel.json`) || **Pass.** No console errors on `/`, `/contact`, `/CONTACT`, `/work`, `/book`, `/me` with the new hash enforced |
| L3 | Lighthouse mobile, local `/` | Perf ≥ 95, A11y 100, BP 100, SEO 100 || **Mixed: A11y, BP and SEO 100 on all 5 runs; Perf 86, 100, 88, 100, 78.** Every dip is Total Blocking Time (470–930 ms) on a page that runs no script (its only `<script>` is JSON-LD). The Mac was loaded (load average 4.4: a VM, the iOS simulator, other sessions), so the dips are the machine, not the page; the clean runs scored 100 with LCP 1.0 s, CLS 0, TBT 0 ms. To recheck when the machine is idle |
| L4 | SEO heads, local | PASS; `/` title 41, description 145; others unchanged || `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`: `/` 41 / 145; `/book` 38 / 133, `/work` 42 / 139, `/contact` and `/CONTACT` 38 / 154 |

Live after deploy `personal-biz-card-6n1wuls8g` (arinakos.com): `/`, `/contact`, `/CONTACT`, `/work` return 200 with
CSP matching `vercel.json` and HTML byte-identical to the build. Live SEO heads `PASS: 5 page(s) measured, 0 failing,
0 warning(s)`. Lighthouse mobile on the live `/` (load average still 4.6): Perf 93, 100, 100; A11y, BP, SEO 100 on all
three; the 93 was again blocking time (310 ms).

## 19 Nov 2026 — `/work` in the homepage's minimal style (predictions written before testing)

Ari: make the products page match the homepage. `/work` now has the homepage header (photo, name and headline, which
link home, plus the Contact card pill), the heading "Products", the intro, and each cluster as a label in the left
column with linked names (↗) and one line each. No screenshots, domains or kind labels. Footer: Home, Contact card,
Book a paid call, LinkedIn. Title and description unchanged.

| # | Test | Prediction | Result |
|---|---|---|---|
| P1 | `/work` at 375×812 and 1280×800, light and dark | No horizontal scroll; text ≥ 18 px; links ≥ 48 px tall; contrast ≥ 4.5:1; reads like the homepage || **Failed first, then pass.** First render: the cluster labels inherited the big serif `h2` style, so on desktop "E-commerce" and "Physical Intelligence" spilled into the text column. Restyled them like the timeline years (18 px sans, muted) in a 190 px column. Then at 375 and 1280, light and dark: no horizontal scroll, smallest text 18 px, no link under 48 px, lowest contrast 6.71:1 light, 7.64:1 dark |
| P2 | CSP enforced locally | Styled, no console errors (new `/work` style hash in `vercel.json`) || **Pass.** No console errors on `/work`, `/`, `/contact`, `/CONTACT`, `/book`, `/me` with the new hash enforced |
| P3 | Lighthouse mobile, local `/work` | A11y, BP, SEO 100; Perf ≥ 95 when the machine isn't loaded (page drops ~89 KB of images) || **Pass.** Five runs (three before the label fix, two after): Perf 100, A11y 100, BP 100, SEO 100 every time (LCP 1.0 s, TBT 0–50 ms). The page dropped its ~89 KB of screenshots (30.2 KB total now) |
| P4 | SEO heads, local | PASS; `/work` title 42, description 139 unchanged; others unchanged || `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`: `/work` 42 / 139 unchanged; `/` 41 / 145, `/book` 38 / 133, `/contact` and `/CONTACT` 38 / 154 |

Live after deploy `personal-biz-card-67y4lz33s` (arinakos.com): `/`, `/work`, `/contact`, `/CONTACT` return 200 with
CSP matching `vercel.json` and HTML byte-identical to the build; the old `/work/*.webp` screenshots now 404. Live SEO
heads `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`. Lighthouse mobile on the live `/work`: 100 / 100 / 100 / 100
on both runs (LCP 1.0–1.1 s, TBT 0 ms).

## 19 Nov 2026 — The Auspicious Company's products on `/work` (predictions written before testing)

Ari: list the products built through The Auspicious Company too. `work.json` now has two sections: "On my own"
(Japanese, E-commerce, Physical Intelligence, unchanged) and "The Auspicious Company" (heading links to the agency):
Education (Setian), Construction (RapidSafeSystems), Privacy (privisay), Health Tech (Mangood, Pomenatal, Outbreak
Files). Each line is taken from the product's own homepage title and description, read today. The page intro, title
and description change because the page is no longer only side projects.

| # | Test | Prediction | Result |
|---|---|---|---|
| A1 | `/work` at 375×812 and 1280×800, light and dark | Both sections read in the same style; no horizontal scroll; text ≥ 18 px; links ≥ 48 px tall (the linked section heading too); contrast ≥ 4.5:1 || **Failed first, then pass.** On a phone the linked heading "The Auspicious Company" wrapped and its ↗ sat at the far edge, then alone on a second line. Fixed by making the link inline and keeping the last word with the arrow (`white-space:nowrap`). Then at 320, 375 and 1280, light and dark: no horizontal scroll, smallest text 18 px, every link ≥ 48 px tall (heading lines 48–52 px), lowest contrast 6.71:1 light, 7.64:1 dark |
| A2 | CSP enforced locally | Styled, no console errors (new `/work` style hash) || **Pass.** No console errors on `/work`, `/`, `/contact`, `/CONTACT`, `/book`, `/me` with the new hash enforced |
| A3 | Lighthouse mobile, local `/work` | Perf ≥ 95 when the machine isn't loaded, A11y 100 (heading order h1 → h2 → h3), BP 100, SEO 100 || **Pass.** Four runs (two before the heading fix, two after): Perf 100, A11y 100 (heading order passes), BP 100, SEO 100 every time; LCP 1.0 s, TBT 0–80 ms |
| A4 | SEO heads, local | PASS; `/work` title 51, description 152; others unchanged || `PASS: 5 page(s) measured, 0 failing, 0 warning(s)`: `/work` 51 / 152; `/` 41 / 145, `/book` 38 / 133, `/contact` and `/CONTACT` 38 / 154 |
| A5 | New outbound links | All six product links and the agency link return 200 with no redirect || **Pass.** Setian, RapidSafeSystems, privisay, Mangood, Pomenatal, Outbreak Files and theauspiciouscompany.com all 200, no redirect. Existing exception: swimmingrhodes.gr redirects to `/el` |

Live after deploy `personal-biz-card-6at1sbqq6` (arinakos.com): `/work`, `/`, `/contact`, `/CONTACT` return 200 with
CSP matching `vercel.json` and HTML byte-identical to the build. Live SEO heads `PASS: 5 page(s) measured, 0 failing,
0 warning(s)` (`/work` 51 / 152). Lighthouse mobile on the live `/work`: Perf 93 then 100 (the 93 was 310 ms of
blocking time on a page with no script); A11y, BP, SEO 100 both runs.

## 19 Nov 2026 — Productivity group with Prodoozie (predictions written before testing)

Ari: rename "Privacy" to "Productivity" and add his second productivity tool, Prodoozie (line from prodoozie.com's
own title and description, read today). Title and description unchanged.

| # | Test | Prediction | Result |
|---|---|---|---|
| R1 | Rebuild, render `/work` at 375 and 1280, light and dark | Only `public/work/index.html` changes (no CSS change, so no new hash); no horizontal scroll; links ≥ 48 px; contrast ≥ 4.5:1 || **Pass.** Only `public/work/index.html` changed (`vercel.json` untouched, same CSS hash). At 375 and 1280, light and dark: no horizontal scroll, smallest text 18 px, no link under 48 px, lowest contrast 6.71:1 light, 7.64:1 dark; no console errors |
| R2 | SEO heads and link check | PASS, `/work` 51 / 152; prodoozie.com returns 200 with no redirect || **Pass.** `PASS: 5 page(s) measured, 0 failing, 0 warning(s)` (`/work` 51 / 152); prodoozie.com 200, no redirect |
