# arinakos.com — personal QR business card

1. Edit your details in `card.json` (name, headline, links, email, phone, which QR style is the card).
2. Rebuild: `.venv/bin/python build.py`. This regenerates the page, the `.vcf`, the images, the QR art, the wallpapers and the Wallet pass. Add `--no-qr` to skip the QR art.
3. Check: `python3 check_seo_heads.py public / /book /work /contact /CONTACT` (title ≤ 60, description ≤ 155).
4. Deploy: `vercel deploy --prod --scope auspicious-co`. Only `public/` and `vercel.json` are uploaded, never `certs/`.
5. Page and contact changes reach people on their next scan. The wallpapers and the Wallet pass are images people already hold, so re-download or re-add those yourself. The printed QR never changes (it's just `HTTPS://ARINAKOS.COM`).

## Paid calls (`/book`)

Calls are booked and paid on Cal.com (event "Consultation", Stripe connected there), so there is no monthly platform fee.
The site only explains the call and links out: no embed, because an embed is a third-party script and the CSP blocks it.

- `booking` in `card.json` holds the label, duration, price, currency, Cal.com URL, a one-line summary (used in the search description), who charges, what it covers, who it's for and the policy.
  From it the build makes `/book`, the "Book a paid call" button on `/`, a "Book a call" link in the `.vcf` (to `/book`, so saved
  contacts keep working if the booking tool changes), the sitemap entry and the `/book` CSP header.
- Set `"booking": null` to remove all of it. The rest of the site builds exactly as before.
- The price on `/book` is typed in `card.json`. If you change it in Cal.com, change it here too and rebuild.
- Check: `python3 check_seo_heads.py public / /book`.

Your own kit, to show the QR, is at `/me`: full-screen QR, the Wallet pass and the wallpapers. Wallet setup is in `APPLE_PASS_SETUP.md`. Tests are in `TEST_LOG.md`.

## Homepage (`/`) and contact card (`/contact`)

`/` is the homepage: photo, name and headline, then the timeline from `timeline.json` (one dot per moment on a vertical
line; each moment has `years`, `title`, optional `note`, and optional `url` + `domain`), then the projects from
`work.json` as a bulleted list. The last moment gets the filled dot. `/contact` is the contact card (Save contact,
every way to reach Ari, and a QR code on request). The QR art, wallpapers, `/me` and the Wallet pass encode
`qr_url` from `card.json` (`HTTPS://ARINAKOS.COM/CONTACT`); `/CONTACT` is rewritten to `/contact` in `vercel.json`.

## Portfolio (`/work`)

`work.json` lists personal ventures outside the agency, in clusters (sections). Each item has a name, URL, domain,
kind, one line and a screenshot in `assets/work/` (720×360 WebP, ~12–21 KB, cropped from the product's live site).
The build makes `/work`, the bulleted "Things I've built" list on `/`, the sitemap entry and the `/work` CSP header.
Delete `work.json` to remove all of it. Keep each line to what the product's own site says.

The name and headings use Brygada 1918 SemiBold (SIL Open Font License, `assets/fonts/OFL.txt`), subset to Latin
(7 KB woff2) and inlined into each page's CSS, so there is no font request; the CSP allows `font-src data:` only.
Design context for future changes is in `.impeccable.md`.
