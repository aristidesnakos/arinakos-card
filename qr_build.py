"""Build the QR art files for the site into public/qr/.

    .venv/bin/python qr_build.py            # uppercase URL from card.json (qr_url)
    .venv/bin/python qr_build.py --lower    # also write lowercase-URL fallbacks, suffix -lower
    .venv/bin/python qr_build.py --test     # decode-test every output afterwards

Writes, per style s in {a, b}:
  qr-s.png (2000 px), qr-s.svg (vector), qr-s-screen.png (1200 px, for /me),
  wallpaper-iphone-s.png (1179x2556), wallpaper-android-s.png (1080x2400).
Idempotent: same inputs give byte-identical files.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import make_qr as mq

OUT = mq.HERE / "public" / "qr"
FONT = "/System/Library/Fonts/SFNS.ttf"
WALLPAPERS = {"iphone": (1179, 2556), "android": (1080, 2400)}
CLOCK_ZONE, BOTTOM_ZONE = 0.38, 0.12         # keep clear: top 38%, bottom 12%
SAFE_MARGIN = 0.012                          # extra air inside that band, fraction of height
SYMBOL_MIN = 0.61                            # QR symbol width / screen width


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def wallpaper(art, W, H):
    """Navy lock screen, white rounded card holding the QR, name + headline under it.
    Returns (image, layout dict) so tests can know where the QR sits."""
    img = Image.new("RGB", (W, H), mq.NAVY)
    d = ImageDraw.Draw(img)
    top, bottom = round(H * (CLOCK_ZONE + SAFE_MARGIN)), round(H * (1 - BOTTOM_ZONE - SAFE_MARGIN))

    # Card = QR incl. its 4-module quiet zone. Whole pixels per grid unit, the smallest size that
    # keeps the symbol (quiet zone excluded) at >= 61% of the screen width.
    upm = art.units_per_module
    ppu = max(1, -(-int(W * SYMBOL_MIN * 1000) // (art.modules * upm * 1000)))
    card = round(art.size * ppu)
    qr = mq.render(art, ppu)

    name_f, head_f = font(round(W * 0.074), "Semibold"), font(round(W * 0.041), "Regular")
    name, head = mq.CARD["name"]["full"], mq.CARD["headline"]
    nb, hb = d.textbbox((0, 0), name, font=name_f, anchor="ls"), d.textbbox((0, 0), head, font=head_f, anchor="ls")
    gap1, rule_gap, gap2 = round(W * 0.062), round(W * 0.032), round(W * 0.034)
    rule_h = max(3, round(W * 0.0034))
    name_cap = -nb[1]                         # ascent above baseline
    head_cap = -hb[1]
    block = card + gap1 + name_cap + rule_gap + rule_h + gap2 + head_cap
    y0 = top + (bottom - top - block) // 2
    if y0 < top:
        raise SystemExit(f"wallpaper {W}x{H}: content ({block}px) doesn't fit the safe band ({bottom - top}px)")

    x0 = (W - card) // 2
    radius = round(W * 0.05)
    d.rounded_rectangle([x0, y0, x0 + card - 1, y0 + card - 1], radius=radius, fill=mq.WHITE)
    mask = Image.new("L", (card, card), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card - 1, card - 1], radius=radius, fill=255)
    img.paste(qr, (x0, y0), mask)

    y = y0 + card + gap1 + name_cap
    d.text((W / 2, y), name, font=name_f, fill=mq.WHITE, anchor="ms")
    y += rule_gap
    rw = round(W * 0.06)
    d.rectangle([(W - rw) // 2, y, (W - rw) // 2 + rw - 1, y + rule_h - 1], fill=mq.GOLD)
    y += rule_h + gap2 + head_cap
    head_col = tuple(round(255 * 0.78 + c * 0.22) for c in mq.NAVY)   # 78% white on navy
    d.text((W / 2, y), head, font=head_f, fill=head_col, anchor="ms")

    mods = art.modules * upm * ppu           # symbol side in px, quiet zone excluded
    layout = {"card_px": card, "card_x": x0, "card_y": y0, "symbol_px": round(mods),
              "symbol_pct_width": round(100 * mods / W, 1), "px_per_module": ppu * upm,
              "content_top_pct": round(100 * y0 / H, 1), "content_bottom_pct": round(100 * y / H, 1)}
    return img, layout


def save_png(img, path):
    img.save(path, "PNG", optimize=True)


def build(lower=False, out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    url = mq.URL.lower() if lower else mq.URL
    sfx = "-lower" if lower else ""
    meta = {"url": url, "files": {}}
    for art in (mq.style_a(url), mq.style_b(url)):
        s = art.name.lower()
        info = {"version": art.version, "modules": art.modules}
        save_png(mq.render_px(art, 2000), out / f"qr-{s}{sfx}.png")
        (out / f"qr-{s}{sfx}.svg").write_text(mq.to_svg(art))
        save_png(mq.render_px(art, 1200), out / f"qr-{s}-screen{sfx}.png")
        for dev, (W, H) in WALLPAPERS.items():
            img, layout = wallpaper(art, W, H)
            save_png(img, out / f"wallpaper-{dev}-{s}{sfx}.png")
            info[f"wallpaper-{dev}"] = layout
        meta["files"][art.name] = info
    return meta


# ---------------------------------------------------------------- tests
def rasterise_svg(svg, px):
    exe = shutil.which("rsvg-convert") or "/opt/homebrew/bin/rsvg-convert"
    if not Path(exe).exists():
        return None
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "r.png"
        subprocess.run([exe, "-w", str(px), "-h", str(px), "-b", "white", "-o", str(png), str(svg)], check=True)
        return Image.open(png).convert("RGB")


def test_all(meta, lower=False, out=OUT):
    url, sfx = meta["url"], "-lower" if lower else ""
    rows = []
    for name, info in meta["files"].items():
        s = name.lower()
        cases = [(f"qr-{s}{sfx}.png", None), (f"qr-{s}-screen{sfx}.png", None)]
        cases += [(f"wallpaper-{d}-{s}{sfx}.png", info[f"wallpaper-{d}"]["card_px"]) for d in WALLPAPERS]
        for f, span in cases:
            rows.append((f, mq.test_image(Image.open(out / f), span, url)))
        svg = out / f"qr-{s}{sfx}.svg"
        r = rasterise_svg(svg, 1200)
        if r is not None:
            rows.append((f"{svg.name} (rsvg 1200px)", mq.test_image(r, None, url)))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lower", action="store_true", help="also emit lowercase-URL fallbacks (-lower suffix)")
    ap.add_argument("--test", action="store_true", help="decode-test every output (3 decoders x clean/blur/dim)")
    ap.add_argument("--json", action="store_true", help="print build metadata as JSON")
    a = ap.parse_args()
    runs = [False] + ([True] if a.lower else [])
    for low in runs:
        meta = build(low)
        if a.json:
            print(json.dumps(meta, indent=1))
        else:
            for k, v in meta["files"].items():
                print(f"style {k} ({meta['url']}): version {v['version']}, {v['modules']}x{v['modules']} modules")
        if a.test:
            for f, res in test_all(meta, low):
                got, tot = mq.score(res)
                per = [sum(v[i] for v in res.values()) for i in range(3)]
                print(f"  {f:38s} {got:2d}/{tot}  zxing {per[0]}/9  zbar {per[1]}/9  opencv {per[2]}/9")
    print(f"wrote {OUT.relative_to(mq.HERE)}/")
