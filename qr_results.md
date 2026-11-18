# QR art results

Encoded URL: `HTTPS://ARINAKOS.COM` (from `card.json` → `qr_url`). Decoders: zxing-cpp, zbar (pyzbar), OpenCV `QRCodeDetector`.
Test: the image is scaled so the QR (including its quiet zone) spans 1200, 400 and 250 px (never upscaled), and each size is decoded clean, Gaussian-blurred (span/400 px) and dimmed (45% brightness, 60% contrast): 9 conditions × 3 decoders = 27.
Predictions were written before each test run.

## 1. `make_qr.py` (uppercase URL)

Prediction: A 27/27 (it was 27/27 lowercase at version 3; uppercase gives bigger modules at version 2). B about 18/27 again (zxing and zbar 9/9, OpenCV 0/9), since the halftone isn't changed by the URL's case.

## 2. `qr_build.py` outputs in `public/qr/` (uppercase URL)

Wallpapers are tested with the QR span set to the white card (QR plus quiet zone), so native size is about 880–960 px, then 400 and 250 px.

Predictions (written before the run):
- `qr-a.png` (2000 px): 27/27, the same art as `make_qr.py` at a larger size.
- `qr-a-screen.png` (1200 px): 27/27.
- `wallpaper-iphone-a.png`, `wallpaper-android-a.png`: 27/27. A navy surround outside the white card might trip OpenCV's finder search, but the card gives a clean quiet zone, so I expect no loss.
- `qr-a.svg` rasterised with `rsvg-convert` (already on the Mac, nothing installed): 27/27.
- `qr-b.png`, `qr-b-screen.png`, `qr-b.svg` raster: 18/27 each (zxing 9, zbar 9, OpenCV 0).
- `wallpaper-iphone-b.png`, `wallpaper-android-b.png`: 18/27, maybe lower at 250 px blur, because B's sub-cells there are only about 1.7 px.
- Lowercase fallbacks (`--lower`): A is version 3 (29×29) and also 27/27; B is unchanged at version 6, 18/27.

## 3. Re-run after one fix: square finder corners on style A

First-run results (before the fix) are kept in section 4. OpenCV missed some A wallpaper conditions (iPhone 8/9, Android 5/9), but the same card cropped on its own was 27/27. The cause is OpenCV losing the finder patterns when the QR is a smaller part of a larger frame: the misses came back with any background (white, navy, grey) once the padding grew. Removing the text, squaring the card or adding 2 more white modules made no difference. Dropping the finder-square corner radius from 0.6 to 0 module fixed it in a side test (OpenCV 9/9 on both wallpapers and on `qr-a.png`).

Prediction for the re-run: every A file 27/27 uppercase, including both wallpapers and the SVG raster. Lowercase A, which was 25/27 with OpenCV missing blur at 400/250 px, also rises to 27/27. B unchanged (B never used rounded finders): square files 17–18/27, wallpapers about 12/27 full-frame, where zbar fails at 400/250 px.

Result: **prediction held.** All results are below.

## 4. Results

### Final run (`make_qr.py`, then `qr_build.py --lower --test`, square finders)

| File | Total | zxing | zbar | OpenCV |
|---|---|---|---|---|
| `make_qr.py` → `qr_A_badge.png` | **27/27** | 9/9 | 9/9 | 9/9 |
| `make_qr.py` → `qr_B_halftone.png` | 18/27 | 9/9 | 9/9 | 0/9 |
| `qr-a.png` (2000 px) | **27/27** | 9/9 | 9/9 | 9/9 |
| `qr-a-screen.png` (1200 px) | **27/27** | 9/9 | 9/9 | 9/9 |
| `wallpaper-iphone-a.png` | **27/27** | 9/9 | 9/9 | 9/9 |
| `wallpaper-android-a.png` | **27/27** | 9/9 | 9/9 | 9/9 |
| `qr-a.svg` (rsvg-convert, 1200 px) | **27/27** | 9/9 | 9/9 | 9/9 |
| `qr-b.png` (2000 px) | 18/27 | 9/9 | 9/9 | 0/9 |
| `qr-b-screen.png` (1200 px) | 17/27 | 9/9 | 8/9 | 0/9 |
| `wallpaper-iphone-b.png` | 12/27 | 9/9 | 3/9 | 0/9 |
| `wallpaper-android-b.png` | 12/27 | 9/9 | 3/9 | 0/9 |
| `qr-b.svg` (rsvg-convert, 1200 px) | 18/27 | 9/9 | 9/9 | 0/9 |
| *lowercase fallbacks (`--lower`)* | | | | |
| `qr-a-lower.png`, `qr-a-screen-lower.png`, both A wallpapers, `qr-a-lower.svg` | 27/27 each | 9/9 | 9/9 | 9/9 |
| `qr-b-lower.png` / `-screen-lower` / `-lower.svg` | 17 / 18 / 18 | 9/9 | 8–9/9 | 0/9 |
| `wallpaper-iphone-b-lower` / `-android-b-lower` | 13 / 12 | 9/9 | 4 / 3 | 0/9 |

B's wallpaper zbar misses are all at the 400 and 250 px spans, where the whole tall frame is scaled down and B's 3×3 sub-cells drop below 3 px. Cropped the way a camera would frame it (card plus a ~12% margin), B's wallpapers read zbar 9/9; OpenCV stays 0/9. I deleted the `-lower` files after the test so the default deploy carries only the ten files below. Run `qr_build.py --lower` to bring them back.

### First run, before the fix (finder corner radius 0.6)

| File | Total | zxing | zbar | OpenCV |
|---|---|---|---|---|
| `wallpaper-iphone-a.png` | 26/27 | 9 | 9 | 8 (missed native-size clean) |
| `wallpaper-android-a.png` | 23/27 | 9 | 9 | 5 (missed 400/250 px clean and dim) |
| `qr-a-lower.png` / `qr-a-lower.svg` | 25/27 | 9 | 9 | 7 (missed blur at 400/250 px) |
| every other A file | 27/27 | | | |

Predictions vs. first run: A's square files and SVG matched (27/27). I predicted no loss on the wallpapers and was wrong, which led to the fix in section 3. B matched on the square files, and its wallpapers came in at the low end I predicted (12/27).

### QR geometry

| Style | URL | Version | Modules | Mode |
|---|---|---|---|---|
| A | `HTTPS://ARINAKOS.COM` | **2** | **25×25** (33×33 with the 4-module quiet zone) | alphanumeric, EC H |
| A | `https://arinakos.com` (fallback) | 3 | 29×29 | byte, EC H |
| B | either | 6 (forced) | 41×41, each split 3×3 → 123×123 sub-cells | EC H |

Wallpaper layout (card = QR plus its 4-module white quiet zone, so the quiet zone is never navy):

| File | Card | QR symbol width | px / module | Content spans (of height) |
|---|---|---|---|---|
| `wallpaper-iphone-a.png` 1179×2556 | 957 px | 725 px = **61.5%** | 29 | 39.4% → 86.7% |
| `wallpaper-android-a.png` 1080×2400 | 891 px | 675 px = **62.5%** | 27 | 39.6% → 86.4% |
| `wallpaper-iphone-b.png` 1179×2556 | 882 px | 738 px = **62.6%** | 18 | 40.8% → 85.2% |
| `wallpaper-android-b.png` 1080×2400 | 882 px | 738 px = **68.3%** | 18 | 39.8% → 86.2% |

Everything sits inside the safe band: below the clock zone (38% plus a 1.2% margin) and above the bottom 12% (minus 1.2%).

### Files (`public/qr/`)

| File | Size |
|---|---|
| `qr-a.png` 2000² | 651 KB |
| `qr-a.svg` (vector dots, square finders, 360 px JPEG photo clipped to a circle) | 28 KB |
| `qr-a-screen.png` 1200² | 319 KB |
| `qr-b.png` 2000² | 230 KB |
| `qr-b.svg` (`<rect>` elements, runs merged, integer coordinates, `crispEdges`) | 60 KB |
| `qr-b-screen.png` 1200² | 197 KB |
| `wallpaper-iphone-a.png` / `-android-a.png` | 127 / 117 KB |
| `wallpaper-iphone-b.png` / `-android-b.png` | 33 / 30 KB |

`qr_build.py` is idempotent: two runs give byte-identical files (checked with `shasum`).

## 5. Visual notes (I looked at every PNG)

- **Fixed:** on the first layout the iPhone-A card started 15 px below the 38% clock line and its headline ended at 87.3%, right at the bottom limit. The card is now the smallest whole-pixel size that keeps the symbol ≥ 61% of the width, the group is centred in a band with a 1.2% margin at each end, and the headline grew from 3.6% to 4.1% of the width (≈ 16 pt on an iPhone). Cards are horizontally centred to the pixel (iPhone A: 111 px each side; B: 148 / 149).
- **Changed for decoding:** A's finder squares are now square-cornered (they were 0.6-module rounded). It still reads as designed next to the round dots, and it's what OpenCV needed (section 3).
- Typography: SF Pro (`SFNS.ttf`) Semibold for the name at 7.4% of the width, a short gold rule (decorative only), and the headline in SF Pro Regular at 78% white. No other text.
- A: the photo is sharp and centred in its gold ring. Dots are cleared within 0.6 module of the photo edge, so the nearest few just touch the ring, which is drawn on top. None looks cut off.
- B: the face reads well at arm's length, but the timing pattern (the dotted line of alternating modules across row 6) cuts across the hairline and forehead. It's a required function pattern and can't be hidden. That's B's main visual flaw.
- The SVGs rasterised with `rsvg-convert` look identical to the PNGs.

## 6. Recommendation (decoders only; Ari's real-phone test decides)

**Style A.** It's 27/27 on every file and both URLs (including both lock-screen wallpapers), version 2 with 25×25 modules, so the dots are big. B is never read by OpenCV, and zbar loses it once the wallpaper is scaled down. Phones with weaker scanners may behave like those decoders. `card.json` already says `"qr_style": "A"`.

### Notes for the coordinator
- `/me`: `qr-a-screen.png` is 319 KB because the photo makes it a full-colour PNG. `qr-a.svg` is 28 KB, decodes 27/27 rasterised, and stays sharp at any size, so it's probably the better choice for `/me`. If you keep the PNG, it's tested as is.
- To rebuild: `.venv/bin/python qr_build.py` (add `--test` to re-score; it needs zbar from Homebrew, which `make_qr.py` finds itself). `build.py` can also `import qr_build; qr_build.build()`.
- Gitignore: none of these outputs need ignoring. `qr_A_badge.png` / `qr_B_halftone.png` in the repo root are `make_qr.py`'s test outputs (regenerated with square finders).
