#!/usr/bin/env python3
"""Measure <title> and meta description length (characters) of each page.
Usage: python3 check_seo_heads.py [base_url_or_dir] [paths...]   default: public/ and "/"
Aim: description <=155 (fail >160), title <=60 (warn >70)."""
import html, re, sys, urllib.request
from pathlib import Path
base = sys.argv[1] if len(sys.argv) > 1 else "public"
paths = sys.argv[2:] or ["/"]
fails = warns = 0
for p in paths:
    if base.startswith("http"):
        src = urllib.request.urlopen(base.rstrip("/") + p).read().decode()
    else:
        f = Path(base) / (p.strip("/") or "index.html")
        if f.is_dir():
            f = f / "index.html"
        elif not f.exists():
            f = f.with_suffix(".html")
        src = f.read_text()
    t = html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip())
    m = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
    d = html.unescape(m.group(1)) if m else ""
    st = "FAIL" if len(t) > 70 else ("WARN" if len(t) > 60 else "ok")
    sd = "FAIL" if len(d) > 160 or not d else ("WARN" if len(d) > 155 else "ok")
    fails += (sd == "FAIL"); warns += (st != "ok") + (sd == "WARN")
    print(f"{p}: title {len(t)} chars [{st}] | description {len(d)} chars [{sd}]")
print(f"{'PASS' if not fails else 'FAIL'}: {len(paths)} page(s) measured, {fails} failing, {warns} warning(s)")
sys.exit(1 if fails else 0)
