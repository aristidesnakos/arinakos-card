# arinakos.com — personal QR business card

1. Edit your details in `card.json` (name, headline, links, email, phone, which QR style is the card).
2. Rebuild: `.venv/bin/python build.py`. This regenerates the page, the `.vcf`, the images, the QR art, the wallpapers and the Wallet pass. Add `--no-qr` to skip the QR art.
3. Check: `python3 check_seo_heads.py public / /book` (title ≤ 60, description ≤ 155).
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
