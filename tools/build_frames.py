#!/usr/bin/env python3
"""Rebuild the frame sections of index.html from frames.json.

Regions between <!--@frames:NAME--> ... <!--/@frames:NAME--> (HTML) and
/*@frames:NAME*/ ... /*/@frames:NAME*/ (JS) are regenerated; everything else is untouched.

Usage:  python3 tools/build_frames.py
"""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "frames.json").read_text(encoding="utf-8"))
FRAMES, GROUPS = DATA["frames"], DATA["groups"]
e = lambda s: html.escape(str(s), quote=True)
js = lambda v: json.dumps(v, ensure_ascii=False)


def tags(ts):
    return "".join(f"<span>{e(t)}</span>" for t in ts)


def region_count():
    return f"<strong>{len(FRAMES)}</strong>"


def region_carousel():
    f0 = FRAMES[0]
    sq = ' class="sq"' if f0.get("logoSquare") else ""
    slides = "\n".join(
        f'              <img{" class=\"on\"" if i == 0 else ""} src="media/{e(f["key"])}.jpg" alt="{e(f["brand"])} {e(f["title"])}">'
        for i, f in enumerate(FRAMES))
    dots = "".join(f'<button{" class=\"on\"" if i == 0 else ""} aria-label="Frame {i+1}"></button>' for i in range(len(FRAMES)))
    return (f'<div class="cinfo" id="cinfo" aria-live="polite">\n'
            f'              <span class="cnum" id="c-num">01 / {len(FRAMES):02d}</span>\n'
            f'              <span class="clogo"><img id="c-logo" src="{e(f0["logo"])}" alt="{e(f0["brand"])}"{sq}></span>\n'
            f'              <b id="c-brand">{e(f0["brand"])}</b>\n'
            f'              <small id="c-camp">{e(f0["campaign"])}</small>\n'
            f'              <span class="ttags" id="c-tags">{tags(f0["tags"])}</span>\n'
            f'            </div>\n'
            f'            <div class="slides">\n{slides}\n            </div>\n'
            f'            <button class="carr l" id="car-prev" aria-label="Previous frame">‹</button>\n'
            f'            <button class="carr r" id="car-next" aria-label="Next frame">›</button>\n'
            f'            <div class="dots" id="car-dots">{dots}</div>')


def region_chips():
    used = []
    for f in FRAMES:
        if f["group"] not in used:
            used.append(f["group"])
    out = ['<button class="chip" data-filter="all" aria-pressed="true">All frames</button>']
    out += [f'<button class="chip" data-filter="{e(g)}" aria-pressed="false">{e(GROUPS.get(g, g))}</button>' for g in used]
    return "\n        ".join(out)


def region_cards():
    cards = []
    for i, f in enumerate(FRAMES):
        cards.append(
            f'<button class="ccard fx" data-open="{i}" data-brand="{e(f["group"])}" data-kw="{e(f["kw"])}" aria-label="Watch {e(f["brand"])} {e(f["title"])}">\n'
            f'          <img src="media/{e(f["key"])}.jpg" alt="" loading="lazy"><video data-key="{e(f["key"])}" muted loop playsinline preload="none"></video>\n'
            f'          <span class="cm">\n'
            f'            <span class="brand"><img src="{e(f["logo"])}" alt="">{e(f["brand"])} · {e(f["campaign"])}</span>\n'
            f'            <h3>{e(f["title"])}</h3>\n'
            f'            <span class="desc">{e(f["desc"])}</span>\n'
            f'            <span class="ttags">{tags(f["tags"])}</span>\n'
            f'            <span class="count">{e(f["duration"])} preview</span>\n'
            f'          </span>\n'
            f'        </button>')
    return "\n        ".join(cards)


def region_results():
    blocks = []
    for f in FRAMES:
        lis = "".join(f"<li>{e(b)}</li>" for b in f["bullets"])
        blocks.append(
            f'        <div class="res fx">\n'
            f'          <h3>{e(f["brand"])} · {e(f.get("resultTitle", f["campaign"]))}</h3>\n'
            f'          <dl><dt>Campaign</dt><dd>{e(f["campaign"])}</dd><dt>Format</dt><dd>{e(f["format"])}</dd></dl>\n'
            f'          <ul>{lis}</ul>\n'
            f'        </div>')
    return '<div class="results">\n' + "\n".join(blocks) + "\n      </div>"


def region_videos():
    rows = ",\n".join(f"    {js(f['key'])}: {{ preview: {js('media/preview/' + f['key'] + '.mp4')}, full: {js('media/' + f['key'] + '.mp4')} }}" for f in FRAMES)
    return "const VIDEOS = {\n" + rows + "\n  };"


def region_tiles():
    return js([f["key"] for f in FRAMES]) + ".forEach(k => { for (let i=0;i<8;i++) T.push(`media/ptiles/${k}-${i}.jpg`); });"


def region_clients():
    rows = ",\n".join("    " + js({"logo": f["logo"], "sq": bool(f.get("logoSquare")), "brand": f["brand"], "camp": f["campaign"], "tags": f["tags"]}) for f in FRAMES)
    return "const CLIENTS = [\n" + rows + "\n  ];"


def region_modal():
    rows = ",\n".join("    " + js({"key": f["key"], "poster": f"media/{f['key']}.jpg", "title": f"{f['brand']}, {f['campaign']}",
                                     "desc": f"{f['desc']} 9:16, {f['duration']} preview."}) for f in FRAMES)
    return "const data = [\n" + rows + "\n  ];"


REGIONS = {"count": region_count, "carousel": region_carousel, "chips": region_chips, "cards": region_cards,
           "results": region_results, "videos": region_videos, "tiles": region_tiles, "clients": region_clients, "modal": region_modal}


def main():
    page = ROOT / "index.html"
    s = page.read_text(encoding="utf-8")
    for name, fn in REGIONS.items():
        for o, c in ((f"<!--@frames:{name}-->", f"<!--/@frames:{name}-->"), (f"/*@frames:{name}*/", f"/*/@frames:{name}*/")):
            if o in s:
                s = re.sub(re.escape(o) + r".*?" + re.escape(c), lambda m: o + fn() + c, s, count=1, flags=re.S)
                break
        else:
            sys.exit(f"marker for region '{name}' not found")
    # every frame needs its media
    missing = [p for f in FRAMES for p in (f"media/{f['key']}.mp4", f"media/{f['key']}.jpg", f"media/preview/{f['key']}.mp4", f"media/ptiles/{f['key']}-0.jpg")
               if not (ROOT / p).exists()]
    if missing:
        sys.exit("missing media: " + ", ".join(missing))
    page.write_text(s, encoding="utf-8")
    print(f"index.html rebuilt with {len(FRAMES)} frames")


if __name__ == "__main__":
    main()
