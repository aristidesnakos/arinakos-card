# arinakos.com — personal QR business card

1. Edit your details in `card.json` (name, headline, links, email, phone, which QR style is the card).
2. Rebuild: `.venv/bin/python build.py`. This regenerates the page, the `.vcf`, the images, the QR art, the wallpapers and the Wallet pass. Add `--no-qr` to skip the QR art.
3. Check: `python3 check_seo_heads.py public /` (title ≤ 60, description ≤ 155).
4. Deploy: `vercel deploy --prod --scope auspicious-co`. Only `public/` and `vercel.json` are uploaded, never `certs/`.
5. Page and contact changes reach people on their next scan. The wallpapers and the Wallet pass are images people already hold, so re-download or re-add those yourself. The printed QR never changes (it's just `HTTPS://ARINAKOS.COM`).

Your own kit, to show the QR, is at `/me`: full-screen QR, the Wallet pass and the wallpapers. Wallet setup is in `APPLE_PASS_SETUP.md`. Tests are in `TEST_LOG.md`.
