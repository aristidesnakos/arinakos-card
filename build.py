#!/usr/bin/env python3
"""Build arinakos.com into public/ from card.json.

    .venv/bin/python build.py            # everything (runs qr_build.py too)
    .venv/bin/python build.py --no-qr    # skip regenerating QR art

Outputs: index.html, me/index.html, the .vcf, images, the Wallet pass (if certs/pass.cer
exists), robots.txt, sitemap.xml and vercel.json (with CSP hashes for the inline code).
"""
import base64, hashlib, html, io, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
SRC, PUB, CERTS = ROOT / "src", ROOT / "public", ROOT / "certs"
card = json.loads((ROOT / "card.json").read_text())

NAME, GIVEN, FAMILY = card["name"]["full"], card["name"]["given"], card["name"]["family"]
HEADLINE, ORG, SITE = card["headline"], card["org"], card["site_url"].rstrip("/")
LINKEDIN, AGENCY = card["links"]["linkedin"], card["links"]["agency"]
EMAIL, PHONE = card.get("email"), card.get("phone")
NAVY, GOLD = card["colors"]["navy"], card["colors"]["gold"]
STYLE = card.get("qr_style", "A").lower()
VCF = "ari-nakos.vcf"
PKPASS = "ari-nakos.pkpass"
PASS_TYPE_ID = "pass.com.arinakos.card"

TITLE = f"{NAME} · {HEADLINE}"
DESC = (f"Save {NAME} to your contacts in one tap. {HEADLINE}, through {ORG}, "
        "including work in regulated sectors.")
OG_DESC = f"Save {NAME} to your contacts in one tap."

PHOTO = Image.open(ROOT / card["photo"]).convert("RGB")


def font(size, weight="Bold"):
    # SF Pro (variable) with a named instance; fall back to Helvetica Neue.
    try:
        f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
        f.set_variation_by_name(weight)
        return f
    except Exception:
        return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1 if weight == "Bold" else 0)


def circle(img, size):
    img = ImageOps.fit(img, (size * 4, size * 4), Image.LANCZOS)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *img.size), fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, mask=mask)
    return out.resize((size, size), Image.LANCZOS)


def ringed(size, ring_px, gap_px, bg):
    """Round photo with a gold ring on `bg` (RGBA canvas of `size`)."""
    s = 4
    big = size * s
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.ellipse((0, 0, big - 1, big - 1), fill=GOLD)
    r = ring_px * s
    d.ellipse((r, r, big - 1 - r, big - 1 - r), fill=bg)
    inner = big - 2 * (r + gap_px * s)
    canvas.alpha_composite(circle(PHOTO, inner // s).resize((inner, inner), Image.LANCZOS), (r + gap_px * s,) * 2)
    return canvas.resize((size, size), Image.LANCZOS)


def b64(img, fmt, **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    return base64.b64encode(buf.getvalue()).decode()


def sha256_csp(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'"


def render(tpl, **kv):
    out = (SRC / tpl).read_text()
    for k, v in kv.items():
        out = out.replace("{{" + k + "}}", v)
    assert "{{" not in out, f"unfilled placeholder in {tpl}"
    return out


# ---------- images ----------
def build_images():
    PUB.mkdir(exist_ok=True)
    # Favicons and touch icons from the photo
    circle(PHOTO, 64).resize((32, 32), Image.LANCZOS).save(PUB / "favicon.ico", sizes=[(32, 32)])
    ImageOps.fit(PHOTO, (180, 180), Image.LANCZOS).save(PUB / "apple-touch-icon.png", optimize=True)
    small = circle(PHOTO, 64)
    (PUB / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><clipPath id="c"><circle cx="32" cy="32" r="32"/></clipPath>'
        f'<image width="64" height="64" clip-path="url(#c)" href="data:image/png;base64,{b64(small, "PNG", optimize=True)}"/></svg>')
    # /me home-screen icons: ringed photo on navy
    for px in (180, 192, 512):
        bg = Image.new("RGBA", (px, px), NAVY)
        rp = int(px * 0.78)
        bg.alpha_composite(ringed(rp, max(2, px // 60), max(2, px // 90), NAVY), ((px - rp) // 2,) * 2)
        bg.convert("RGB").save(PUB / f"me-icon-{px}.png", optimize=True)

    # OG image 1200x630
    W, H = 1200, 630
    og = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(og)
    ph = 360
    og.alpha_composite(ringed(ph, 8, 8, NAVY), (110, (H - ph) // 2))
    x = 110 + ph + 70
    d.text((x, 200), NAME, font=font(84, "Bold"), fill="white")
    hf = font(40, "Regular")
    words, lines, cur = HEADLINE.split(), [], ""
    for w in words:  # wrap headline to fit
        t = (cur + " " + w).strip()
        if d.textlength(t, font=hf) > W - x - 80 and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    y = 312
    for ln in lines:
        d.text((x, y), ln, font=hf, fill=(220, 225, 235)); y += 52
    d.rectangle((x, y + 26, x + 64, y + 30), fill=GOLD)
    d.text((x, y + 52), "arinakos.com", font=font(34, "Semibold"), fill=GOLD)
    og.convert("RGB").save(PUB / "og.png", optimize=True)

    avatar = ImageOps.fit(PHOTO, (304, 304), Image.LANCZOS)
    return "data:image/webp;base64," + b64(avatar, "WEBP", quality=78, method=6)


# ---------- vCard ----------
def vfold(line):
    """Fold at 75 octets per RFC 2425/2426; continuation lines start with one space."""
    raw = line.encode()
    if len(raw) <= 75:
        return line
    parts, first = [], True
    while raw:
        n = 75 if first else 74
        cut = n
        while cut < len(raw) and (raw[cut] & 0xC0) == 0x80:  # don't split UTF-8 sequences
            cut -= 1
        parts.append(("" if first else " ") + raw[:cut].decode())
        raw, first = raw[cut:], False
    return "\r\n".join(parts)


def vesc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def build_vcf():
    photo = ImageOps.fit(PHOTO, (360, 360), Image.LANCZOS)
    lines = [
        "BEGIN:VCARD", "VERSION:3.0",
        f"N:{vesc(FAMILY)};{vesc(GIVEN)};;;", f"FN:{vesc(NAME)}",
        f"ORG:{vesc(ORG)}", f"TITLE:{vesc(HEADLINE)}",
    ]
    if EMAIL:
        lines.append(f"EMAIL;type=INTERNET;type=WORK;type=pref:{EMAIL}")
    if PHONE:
        lines.append(f"TEL;type=CELL;type=VOICE;type=pref:{PHONE}")
    lines += [
        f"item1.URL;type=pref:{LINKEDIN}", "item1.X-ABLabel:LinkedIn",
        f"X-SOCIALPROFILE;type=linkedin:{LINKEDIN}",
        f"item2.URL:{AGENCY}", f"item2.X-ABLabel:{vesc(ORG)}",
        f"item3.URL:{SITE}", "item3.X-ABLabel:Card",
        f"PHOTO;ENCODING=b;TYPE=JPEG:{b64(photo, 'JPEG', quality=80, optimize=True, progressive=False)}",
        "END:VCARD",
    ]
    text = "\r\n".join(vfold(l) for l in lines) + "\r\n"
    (PUB / VCF).write_bytes(text.encode())
    return len(text)


# ---------- Wallet pass ----------
def build_pass():
    cer = CERTS / "pass.cer"
    if not cer.exists():
        print("pass: skipped (certs/pass.cer not found; see APPLE_PASS_SETUP.md)")
        (PUB / PKPASS).unlink(missing_ok=True)
        return False
    tmp = Path(tempfile.mkdtemp())
    try:
        pem = tmp / "pass.pem"; wwdr = tmp / "wwdr.pem"
        subprocess.run(["openssl", "x509", "-inform", "der", "-in", cer, "-out", pem], check=True)
        subprocess.run(["openssl", "x509", "-inform", "der", "-in", CERTS / "AppleWWDRCAG4.cer", "-out", wwdr], check=True)
        subj = subprocess.run(["openssl", "x509", "-in", pem, "-noout", "-subject", "-nameopt", "multiline"],
                              capture_output=True, text=True, check=True).stdout
        team = next(l.split("=", 1)[1].strip() for l in subj.splitlines() if "organizationalUnitName" in l)
        uid = next((l.split("=", 1)[1].strip() for l in subj.splitlines() if "userId" in l), PASS_TYPE_ID)
        files = {}
        rgb = lambda h: "rgb({},{},{})".format(*(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)))
        back = [{"key": "linkedin", "label": "LinkedIn", "value": LINKEDIN},
                {"key": "agency", "label": ORG, "value": AGENCY}]
        if EMAIL:
            back.insert(0, {"key": "email", "label": "Email", "value": EMAIL})
        back.append({"key": "site", "label": "Card", "value": SITE})
        barcode = {"format": "PKBarcodeFormatQR", "message": card["qr_url"],
                   "messageEncoding": "iso-8859-1", "altText": "arinakos.com"}
        pj = {
            "formatVersion": 1, "passTypeIdentifier": uid, "teamIdentifier": team,
            "serialNumber": "arinakos-card-1", "organizationName": NAME,
            "description": f"{NAME} business card", "logoText": "arinakos.com",
            "foregroundColor": "rgb(255,255,255)", "backgroundColor": rgb(NAVY), "labelColor": "rgb(224,176,79)",
            "generic": {
                "primaryFields": [{"key": "name", "label": "", "value": NAME}],
                "secondaryFields": [{"key": "headline", "label": "", "value": HEADLINE}],
                "auxiliaryFields": [{"key": "org", "label": "Agency", "value": ORG}],
                "backFields": back,
            },
            "barcodes": [barcode], "barcode": barcode,
        }
        files["pass.json"] = json.dumps(pj, indent=1).encode()
        for scale, sfx in ((1, ""), (2, "@2x"), (3, "@3x")):
            files[f"icon{sfx}.png"] = png_bytes(ringed(29 * scale, scale, scale, NAVY), NAVY)
            files[f"thumbnail{sfx}.png"] = png_bytes(ringed(90 * scale, 2 * scale, 2 * scale, NAVY), None)
        manifest = {k: hashlib.sha1(v).hexdigest() for k, v in files.items()}
        files["manifest.json"] = json.dumps(manifest).encode()
        (tmp / "manifest.json").write_bytes(files["manifest.json"])
        subprocess.run(["openssl", "smime", "-binary", "-sign", "-certfile", wwdr, "-signer", pem,
                        "-inkey", CERTS / "pass.key", "-in", tmp / "manifest.json",
                        "-out", tmp / "signature", "-outform", "DER"], check=True)
        files["signature"] = (tmp / "signature").read_bytes()
        with zipfile.ZipFile(PUB / PKPASS, "w", zipfile.ZIP_DEFLATED) as z:
            for k, v in files.items():
                z.writestr(k, v)
        print(f"pass: built {PKPASS} (team {team})")
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def png_bytes(img, bg):
    if bg:
        base = Image.new("RGBA", img.size, bg); base.alpha_composite(img); img = base.convert("RGB")
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True); return buf.getvalue()


# ---------- pages ----------
ICONS = {
    "linkedin": '<svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 10.5V17M8 7.5v.01M12 17v-3.6a2.4 2.4 0 0 1 4.8 0V17M12 10.5V17"/></svg>',
    "email": '<svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/></svg>',
    "phone": '<svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22"><path d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "web": '<svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
}

INDEX_JS = """(function(){var ua=navigator.userAgent||"";if(/FBAN|FBAV|Instagram|LinkedInApp|Line\\/|Snapchat|TikTok|musical_ly/i.test(ua)){document.getElementById("hint").hidden=false}})();"""

ME_JS = """(function(){var l=null;function g(){if("wakeLock"in navigator&&document.visibilityState==="visible"){navigator.wakeLock.request("screen").then(function(x){l=x}).catch(function(){})}}g();document.addEventListener("visibilitychange",g)})();"""


def build_pages(avatar, has_pass):
    sec = [f'<a class="btn" href="{LINKEDIN}" rel="me noopener">{ICONS["linkedin"]}<span>LinkedIn</span></a>']
    if EMAIL:
        sec.append(f'<a class="btn" href="mailto:{EMAIL}">{ICONS["email"]}<span>Email</span></a>')
    if PHONE:
        sec.append(f'<a class="btn" href="tel:{PHONE.replace(" ", "")}">{ICONS["phone"]}<span>Call</span></a>')
    sec.append(f'<a class="btn" href="{AGENCY}" rel="noopener">{ICONS["web"]}<span>{html.escape(ORG)}</span></a>')

    person = {"@context": "https://schema.org", "@type": "Person", "name": NAME, "givenName": GIVEN,
              "familyName": FAMILY, "jobTitle": HEADLINE, "url": SITE + "/", "image": SITE + "/og.png",
              "worksFor": {"@type": "Organization", "name": ORG, "url": AGENCY},
              "sameAs": [LINKEDIN, AGENCY]}
    if EMAIL:
        person["email"] = "mailto:" + EMAIL
    css = (SRC / "style.css").read_text().strip()
    index = render("index.html", TITLE=html.escape(TITLE), DESC=html.escape(DESC), OG_DESC=html.escape(OG_DESC),
                   SITE=SITE, NAME=html.escape(NAME), GIVEN=GIVEN, FAMILY=FAMILY, HEADLINE=html.escape(HEADLINE),
                   JSONLD=json.dumps(person, ensure_ascii=False).replace("</", "<\\/"), CSS=css, AVATAR=avatar,
                   VCF=VCF, SECONDARY="\n    ".join(sec), JS=INDEX_JS)
    (PUB / "index.html").write_text(index)

    kit = []
    if has_pass:
        kit.append(f'<li><a href="/{PKPASS}">Add to Apple Wallet</a></li>')
    for label, f in (("iPhone lock-screen wallpaper", f"wallpaper-iphone-{STYLE}.png"),
                     ("Android lock-screen wallpaper", f"wallpaper-android-{STYLE}.png"),
                     ("QR code, PNG (print)", f"qr-{STYLE}.png"), ("QR code, SVG (print)", f"qr-{STYLE}.svg")):
        if (PUB / "qr" / f).exists():
            kit.append(f'<li><a href="/qr/{f}" download>{label}</a></li>')
    (PUB / "me").mkdir(exist_ok=True)
    (PUB / "me" / "index.html").write_text(render("me.html", NAME=html.escape(NAME), QR_SCREEN=f"qr-{STYLE}.svg",
                                                   KIT="\n    ".join(kit), JS=ME_JS))
    (PUB / "me.webmanifest").write_text(json.dumps({
        "name": f"{NAME} card", "short_name": "Card", "start_url": "/me", "scope": "/me", "display": "standalone",
        "background_color": "#FFFFFF", "theme_color": "#FFFFFF",
        "icons": [{"src": "/me-icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/me-icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1))
    (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (PUB / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{SITE}/</loc></url></urlset>\n")
    return css


def build_vercel_json(css):
    base = ["default-src 'none'", "img-src 'self' data:", "connect-src 'self'", "manifest-src 'self'",
            "base-uri 'none'", "form-action 'none'", "frame-ancestors 'none'"]
    me_css = (PUB / "me" / "index.html").read_text().split("<style>")[1].split("</style>")[0]
    csp_index = "; ".join(base + [f"style-src {sha256_csp(css)}", f"script-src {sha256_csp(INDEX_JS)}"])
    csp_me = "; ".join(base + [f"style-src {sha256_csp(me_css)}", f"script-src {sha256_csp(ME_JS)}"])
    common = [{"key": "X-Content-Type-Options", "value": "nosniff"},
              {"key": "Referrer-Policy", "value": "no-referrer"},
              {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), interest-cohort=()"},
              {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"}]
    revalidate = {"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}
    cfg = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "framework": None, "buildCommand": None, "installCommand": None, "outputDirectory": "public",
        "cleanUrls": True, "trailingSlash": False,
        "headers": [
            {"source": "/(.*)", "headers": common},
            {"source": "/", "headers": [{"key": "Content-Security-Policy", "value": csp_index}, revalidate]},
            {"source": "/me", "headers": [{"key": "Content-Security-Policy", "value": csp_me}, revalidate]},
            {"source": f"/{VCF}", "headers": [
                {"key": "Content-Type", "value": "text/vcard; charset=utf-8"},
                {"key": "Content-Disposition", "value": f'inline; filename="{VCF}"'}, revalidate]},
            {"source": f"/{PKPASS}", "headers": [
                {"key": "Content-Type", "value": "application/vnd.apple.pkpass"},
                {"key": "Content-Disposition", "value": f'attachment; filename="{PKPASS}"'}, revalidate]},
            {"source": "/me.webmanifest", "headers": [{"key": "Content-Type", "value": "application/manifest+json"}]},
        ],
    }
    (ROOT / "vercel.json").write_text(json.dumps(cfg, indent=2) + "\n")


def main():
    if "--no-qr" not in sys.argv and (ROOT / "qr_build.py").exists():
        subprocess.run([sys.executable, str(ROOT / "qr_build.py")], check=True, cwd=ROOT)
    avatar = build_images()
    n = build_vcf()
    has_pass = build_pass()
    css = build_pages(avatar, has_pass)
    build_vercel_json(css)
    size = (PUB / "index.html").stat().st_size
    print(f"built: index.html {size/1024:.1f} KB, {VCF} {n/1024:.1f} KB, title {len(TITLE)} chars, description {len(DESC)} chars")


if __name__ == "__main__":
    main()
