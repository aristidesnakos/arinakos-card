"""Styled QR codes for the card, made in code (no AI art), plus a 3-decoder test.

The URL, name and colours come from card.json (read only). Each style is built as
vector geometry in grid units, so the same art renders to PNG (any size) and SVG.

  Style A: navy round dots, square finder patterns, photo in a gold-ringed centre circle.
  Style B: halftone, every module split 3x3; the centre sub-cell carries the data and the
           other eight draw the face. Forced to version 6 so there are enough dots.

Run `.venv/bin/python make_qr.py` to write qr_A_badge.png / qr_B_halftone.png and score
them: 3 sizes x 3 conditions (clean, blur, dim) x 3 decoders (zxing, zbar, opencv) = 27.
"""
import base64, io, json, os, sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np, segno, cv2, zxingcpp
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter

if sys.platform == "darwin" and "/opt/homebrew/lib" not in os.environ.get("DYLD_LIBRARY_PATH", ""):
    os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
try:
    from pyzbar import pyzbar
except ImportError:  # zbar not found by ctypes: load it from Homebrew directly
    import ctypes.util
    _orig = ctypes.util.find_library
    ctypes.util.find_library = lambda n: "/opt/homebrew/lib/libzbar.dylib" if n == "zbar" else _orig(n)
    from pyzbar import pyzbar

HERE = Path(__file__).resolve().parent
CARD = json.loads((HERE / "card.json").read_text())
URL = CARD["qr_url"]                       # HTTPS://ARINAKOS.COM (uppercase -> alphanumeric mode)
PHOTO = HERE / CARD["photo"]


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


NAVY_HEX, GOLD_HEX, WHITE_HEX = CARD["colors"]["navy"], CARD["colors"]["gold"], CARD["colors"]["white"]
NAVY, GOLD, WHITE = _hex(NAVY_HEX), _hex(GOLD_HEX), _hex(WHITE_HEX)
QUIET = 4                                  # quiet zone, modules


# ---------------------------------------------------------------- QR matrix
def matrix(url=URL, version=None):
    q = segno.make(url, error="h", version=version, micro=False, boost_error=False)
    m = np.array([[bool(c) for c in row] for row in q.matrix])
    return q, m


def function_mask(n, version):
    """True where a module is part of finder/separator, timing or alignment patterns."""
    f = np.zeros((n, n), bool)
    for r, c in [(0, 0), (0, n - 8), (n - 8, 0)]:
        f[r:r + 8, c:c + 8] = True
    f[6, :] = True
    f[:, 6] = True
    if 2 <= version <= 6:                  # one alignment pattern at (n-7, n-7)
        a = n - 7
        f[a - 2:a + 3, a - 2:a + 3] = True
    return f


def in_finder(r, c, n):
    return r < 8 and (c < 8 or c >= n - 8) or (r >= n - 8 and c < 8)


def face(size):
    im = Image.open(PHOTO).convert("RGB")
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, 0, (w - s) // 2 + s, s)).resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- geometry
@dataclass
class Art:
    """Vector QR art. All coordinates are in grid units; the canvas is size x size units."""
    name: str
    size: float                            # canvas side in grid units (includes the quiet zone)
    units_per_module: int
    version: int
    modules: int                           # symbol side in modules (no quiet zone)
    circles: list = field(default_factory=list)   # (cx, cy, r, rgb)
    rects: list = field(default_factory=list)     # (x, y, w, h, rx, rgb)
    photo: tuple | None = None             # (cx, cy, r) photo clipped to a circle
    ring: tuple | None = None              # (cx, cy, r_inner, width, rgb) gold ring outside photo
    crisp: bool = False                    # axis-aligned only: render without anti-aliasing


FINDER_RX = 0.0   # corner radius of the finder squares, modules (spec: <= 0.6). 0.6 cost OpenCV
                  # 1-4 of 9 reads on the lock-screen wallpapers; square corners read 9/9 everywhere.


def _finder_rects(art, r, c, u=1.0):
    x, y = (c + QUIET) * u, (r + QUIET) * u
    rx = FINDER_RX * u
    art.rects += [(x, y, 7 * u, 7 * u, rx, NAVY),
                  (x + u, y + u, 5 * u, 5 * u, rx / 2, WHITE),
                  (x + 2 * u, y + 2 * u, 3 * u, 3 * u, rx / 2, NAVY)]


def style_a(url=URL):
    q, m = matrix(url)
    n = len(m)
    art = Art("A", n + 2 * QUIET, 1, q.version, n)
    c0 = (n - 1) / 2
    cr = n * 0.15                          # photo radius, modules
    for r in range(n):
        for c in range(n):
            if in_finder(r, c, n) or not m[r, c]:
                continue
            if ((r - c0) ** 2 + (c - c0) ** 2) ** 0.5 < cr + 0.6:
                continue                   # cleared for the photo; EC level H rebuilds it
            art.circles.append((c + QUIET + 0.5, r + QUIET + 0.5, 0.42, NAVY))
    for r, c in [(0, 0), (0, n - 7), (n - 7, 0)]:
        _finder_rects(art, r, c)
    cx = c0 + QUIET + 0.5
    art.photo = (cx, cx, cr)
    art.ring = (cx, cx, cr, 0.35, GOLD)
    return art


def _merge_runs(grid):
    """Boolean grid -> list of (x, y, w, h) rectangles covering the True cells."""
    rows, cols = grid.shape
    open_runs, out = {}, []
    for y in range(rows + 1):
        runs = set()
        if y < rows:
            row, x = grid[y], 0
            while x < cols:
                if row[x]:
                    x0 = x
                    while x < cols and row[x]:
                        x += 1
                    runs.add((x0, x - x0))
                else:
                    x += 1
        nxt = {}
        for k, (y0, h) in open_runs.items():
            if k in runs:
                nxt[k] = (y0, h + 1)
            else:
                out.append((k[0], y0, k[1], h))
        for k in runs:
            nxt.setdefault(k, (y, 1))
        open_runs = nxt
    return sorted(out, key=lambda t: (t[1], t[0]))


def style_b(url=URL, version=6):
    q, m = matrix(url, version)
    n = len(m)
    sub = 3
    g = face(n * sub).convert("L")
    g = ImageOps.autocontrast(g, cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.4)
    arr = np.asarray(g, dtype=float) / 255
    arr = np.where(arr > 0.72, 1.0, arr)   # clean near-white wall
    bayer = np.array([[0, 6, 3], [8, 4, 7], [2, 5, 1]]) / 9 + 1 / 18
    dots = arr < np.tile(bayer, (n, n))
    fm = function_mask(n, q.version)
    N = (n + 2 * QUIET) * sub
    grid = np.zeros((N, N), bool)
    for r in range(n):
        for c in range(n):
            y0, x0 = (r + QUIET) * sub, (c + QUIET) * sub
            if fm[r, c]:
                grid[y0:y0 + sub, x0:x0 + sub] = m[r, c]
                continue
            block = dots[r * sub:(r + 1) * sub, c * sub:(c + 1) * sub].copy()
            block[1, 1] = m[r, c]
            grid[y0:y0 + sub, x0:x0 + sub] = block
    art = Art("B", N, sub, q.version, n, crisp=True)
    art.rects = [(x, y, w, h, 0, NAVY) for x, y, w, h in _merge_runs(grid)]
    return art


# ---------------------------------------------------------------- renderers
def render(art, px_per_unit, ss=None):
    """Render to an RGB image of side round(art.size * px_per_unit)."""
    side = round(art.size * px_per_unit)
    if ss is None:
        ss = 1 if (art.crisp and float(px_per_unit).is_integer()) else 4
    s = px_per_unit * ss
    big = Image.new("RGB", (round(art.size * s),) * 2, WHITE)
    d = ImageDraw.Draw(big)
    for x, y, w, h, rx, col in art.rects:
        box = [round(x * s), round(y * s), round((x + w) * s) - 1, round((y + h) * s) - 1]
        if rx:
            d.rounded_rectangle(box, radius=rx * s, fill=col)
        else:
            d.rectangle(box, fill=col)
    for cx, cy, r, col in art.circles:
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=col)
    if art.photo:
        cx, cy, r = art.photo
        D = round(2 * r * s)
        mask = Image.new("L", (D, D), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, D - 1, D - 1], fill=255)
        big.paste(face(D), (round(cx * s) - D // 2, round(cy * s) - D // 2), mask)
    if art.ring:
        cx, cy, ri, w, col = art.ring
        ro = ri + w
        d.ellipse([(cx - ro) * s, (cy - ro) * s, (cx + ro) * s, (cy + ro) * s], outline=col, width=round(w * s))
    return big if big.size[0] == side else big.resize((side, side), Image.LANCZOS)


def render_px(art, side_px):
    """Render at an exact pixel side (resampled if side_px isn't a whole multiple of the grid)."""
    ppu = side_px / art.size
    if art.crisp:
        img = render(art, max(1, int(np.ceil(ppu))), ss=1)
    else:
        img = render(art, int(np.ceil(ppu)), ss=3)
    return img if img.size[0] == side_px else img.resize((side_px, side_px), Image.LANCZOS)


def _f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s[1:] if s.startswith("0.") else s or "0"


def to_svg(art, photo_px=360):
    """True vector SVG. The photo (style A) is a base64 JPEG clipped to its circle."""
    n = art.size
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_f(n)} {_f(n)}" '
           f'width="{_f(n * 20 / art.units_per_module)}" height="{_f(n * 20 / art.units_per_module)}"'
           + (' shape-rendering="crispEdges"' if art.crisp else "") + ">",
           f'<rect width="{_f(n)}" height="{_f(n)}" fill="{WHITE_HEX}"/>']
    by_col = {}
    for x, y, w, h, rx, col in art.rects:
        by_col.setdefault(col, []).append(
            f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}"' + (f' rx="{_f(rx)}"' if rx else "") + "/>")
    # keep finder layering: draw rects in their original order when colours interleave
    if len(by_col) > 1:
        for x, y, w, h, rx, col in art.rects:
            out.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}"'
                       + (f' rx="{_f(rx)}"' if rx else "") + f' fill="#{"%02X%02X%02X" % col}"/>')
    elif by_col:
        col = next(iter(by_col))
        out.append(f'<g fill="#{"%02X%02X%02X" % col}">' + "".join(by_col[col]) + "</g>")
    if art.circles:
        col = art.circles[0][3]
        out.append(f'<g fill="#{"%02X%02X%02X" % col}">'
                   + "".join(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}"/>' for cx, cy, r, _ in art.circles)
                   + "</g>")
    if art.photo:
        cx, cy, r = art.photo
        buf = io.BytesIO()
        face(photo_px).save(buf, "JPEG", quality=82, optimize=True, progressive=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        out.append(f'<clipPath id="ph"><circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}"/></clipPath>'
                   f'<image href="data:image/jpeg;base64,{b64}" x="{_f(cx - r)}" y="{_f(cy - r)}" '
                   f'width="{_f(2 * r)}" height="{_f(2 * r)}" clip-path="url(#ph)"/>')
    if art.ring:
        cx, cy, ri, w, col = art.ring
        out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(ri + w / 2)}" fill="none" '
                   f'stroke="#{"%02X%02X%02X" % col}" stroke-width="{_f(w)}"/>')
    out.append("</svg>\n")
    return "\n".join(out)


# ---------------------------------------------------------------- decode test
DECODERS = ("zxing", "zbar", "opencv")
CONDITIONS = ("clean", "blur", "dim")


def decode(im, url=URL):
    """[zxing, zbar, opencv] -> True if that decoder read `url` (case-insensitive)."""
    want = url.lower()
    a = np.asarray(im.convert("RGB"))
    ok = [any(b.text.lower() == want for b in zxingcpp.read_barcodes(a)),
          any(b.data.decode(errors="replace").lower() == want for b in pyzbar.decode(im.convert("RGB")))]
    try:
        t, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(a, cv2.COLOR_RGB2BGR))
    except cv2.error:
        t = ""
    ok.append((t or "").lower() == want)
    return ok


def test_image(base, qr_span_px=None, url=URL, spans=(1200, 400, 250)):
    """Scale so the QR (incl. quiet zone) spans 1200/400/250 px (never upscaled), then decode
    clean, Gaussian-blurred (span/400) and dimmed (45% brightness, 60% contrast)."""
    base = base.convert("RGB")
    qr_span_px = qr_span_px or min(base.size)
    results = {}
    for span in spans:
        k = min(1.0, span / qr_span_px)
        im0 = base.resize((max(1, round(base.width * k)), max(1, round(base.height * k))), Image.LANCZOS) if k < 1 else base
        eff = round(qr_span_px * k)
        for cond in CONDITIONS:
            im = im0
            if cond == "blur":
                im = im.filter(ImageFilter.GaussianBlur(eff / 400))
            if cond == "dim":
                im = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(0.45)).enhance(0.6)
            results[f"{eff}px-{cond}"] = decode(im, url)
    return results


def score(res):
    return sum(sum(v) for v in res.values()), 3 * len(res)


def report(label, res):
    got, total = score(res)
    lines = [f"{label}: {got}/{total} decodes  [zxing, zbar, opencv]"]
    lines += [f"  {k:14s} {['ok' if x else '--' for x in v]}" for k, v in res.items()]
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"URL from card.json: {URL}")
    for art, f in ((style_a(), "qr_A_badge.png"), (style_b(), "qr_B_halftone.png")):
        img = render(art, 40) if art.name == "A" else render(art, 14, ss=1)   # 40 px/module, 42 px/module
        img.save(HERE / f)
        print(f"\nstyle {art.name}: version {art.version}, {art.modules}x{art.modules} modules")
        print(report(f, test_image(img)))
