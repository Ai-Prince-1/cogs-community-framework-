"""Build the COGS website from the Markdown in this repo.

    pip install markdown
    python site/build.py          # writes _site/
    python -m http.server -d _site

The Markdown files stay the single source of truth. GitHub Actions runs this
on every push to main and publishes _site/ to GitHub Pages.
"""
import html
import re
import shutil
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent
OUT = ROOT / "_site"
REPO_URL = "https://github.com/Ai-Prince-1/cogs-community-framework-"

# Library: (section, [(source path, page title, one-line summary)])
LIBRARY = [
    ("Foundations", [
        ("docs/manifesto.md", "Manifesto", "Why COGS exists and what it stands for."),
        ("docs/constitution.md", "Constitution", "The governance rules every Circle shares."),
        ("docs/handbook.md", "Circle Handbook", "Everything a Circle needs to start, run, grow and self-correct."),
    ]),
    ("Playbooks", [
        ("playbooks/circle-launch.md", "Launch a Circle", "Start your first Circle in one evening."),
        ("playbooks/conflict-resolution.md", "Conflict Resolution", "A three-level protocol for disagreements."),
        ("playbooks/seeding-ceremony.md", "Seeding Ceremony", "How a Circle that has grown too big splits well."),
    ]),
    ("Meetings", [
        ("meetings/weekly-gathering.md", "Weekly Gathering", "The 70-minute heartbeat of every Circle."),
        ("meetings/season-opening.md", "Season Opening", "Week 1: choose domains, set intentions."),
        ("meetings/mid-season-checkin.md", "Mid-Season Check-In", "Week 6: adjust course."),
        ("meetings/retrospective.md", "Season Retrospective", "Week 12: celebrate and self-correct."),
        ("meetings/season-review.md", "Season Review", "The one-page Season Summary."),
    ]),
    ("Roles", [
        ("roles/facilitator.md", "Facilitator", "Holds the time and the space. Rotates weekly."),
        ("roles/steward.md", "Steward", "Keeps the transparent ledger when a Circle pools resources."),
        ("roles/scribe.md", "Scribe", "Keeps the Circle's memory."),
        ("roles/bridge.md", "Bridge", "Connects a Circle to its Mesh."),
    ]),
    ("Reference", [
        ("docs/anti-cult-safeguards.md", "Anti-Cult Safeguards", "How COGS stays open and self-correcting."),
        ("docs/glossary.md", "Glossary", "Every COGS term in one place."),
        ("branding/assets.md", "Brand Assets", "The logo, what it means and how to use it."),
    ]),
    ("Contribute", [
        ("CONTRIBUTING.md", "Contributing", "How to suggest a change."),
        ("rfc/README.md", "RFC Process", "How bigger changes are proposed and decided."),
        ("rfc/template.md", "RFC Template", "Start a proposal here."),
        ("CHANGELOG.md", "Changelog", "What changed in each version."),
    ]),
]

PAGES = [(sec, src, title, blurb) for sec, items in LIBRARY for (src, title, blurb) in items]
SLUG = {src: re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") + ".html" for _, src, title, _ in PAGES}


def clean_heading(text: str) -> str:
    """'— Part I  ·  Something is wrong —' -> 'Part I: Something is wrong'."""
    t = text.strip().strip("—").strip()
    t = re.sub(r"\s+·\s+", ": ", t, count=1) if t.lower().startswith(("part", "section")) else t
    return t


def rewrite_links(md_text: str, src: str) -> str:
    """Point links between Markdown files at the generated pages."""
    base = (ROOT / src).parent

    def repl(m):
        label, target, anchor = m.group(1), m.group(2), m.group(3) or ""
        if target.startswith(("http", "mailto", "#")):
            return m.group(0)
        resolved = (base / target).resolve()
        try:
            rel = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        if rel in SLUG:
            return f"[{label}]({SLUG[rel]}{anchor})"
        if rel == "README.md":
            return f"[{label}](index.html{anchor})"
        if resolved.is_file() and resolved.suffix.lower() in {".jpg", ".png", ".svg"}:
            return f"[{label}](assets/{resolved.name})"
        if rel == "LICENSE":
            return f"[{label}]({REPO_URL}/blob/main/LICENSE)"
        return f"[{label}]({REPO_URL}/blob/main/{rel})"

    return re.sub(r"\[([^\]]+)\]\(([^)#\s]*)(#[^)\s]*)?\)", repl, md_text)


def strip_cover(raw: str) -> str:
    """Drop a title block (subtitle headings, tagline, version line) that ends
    in '---' near the top; the page header already shows that information."""
    lines = raw.split("\n")
    for i, line in enumerate(lines[:14]):
        if line.strip() == "---":
            head = [l.strip() for l in lines[:i] if l.strip()]
            if head and all(l.startswith(("#", "*", ">", "_")) and not l.startswith(("* ", "- ")) for l in head):
                return "\n".join(lines[i + 1:])
            break
    return raw


LIST_ITEM = re.compile(r"^\s*([*+-]|\d+\.)\s+")


def fix_lists(raw: str) -> str:
    """Markdown needs a blank line before a list; many source files omit it."""
    out, fenced = [], False
    for line in raw.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
        prev = out[-1] if out else ""
        if (not fenced and LIST_ITEM.match(line) and prev.strip()
                and not LIST_ITEM.match(prev) and not prev.startswith((" ", "\t", "|", ">"))):
            out.append("")
        out.append(line)
    return "\n".join(out)


def render(src: str):
    raw = (ROOT / src).read_text(encoding="utf-8")
    raw = rewrite_links(raw, src)
    # Drop the document's own H1 (the page shows its title) and leading meta lines
    raw = re.sub(r"\A\s*# [^\n]*\n", "", raw, count=1)
    raw = strip_cover(raw)
    raw = fix_lists(raw)
    # Make headings like "## — Part I  ·  Something is wrong —" read cleanly
    raw = re.sub(r"^(#{2,6}) (.+)$", lambda m: f"{m.group(1)} {clean_heading(m.group(2))}", raw, flags=re.M)
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list"],
                           extension_configs={"toc": {"toc_depth": "2-2", "slugify": slugify}})
    body = md.convert(raw)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    return body, toc


def nav_html(active: str) -> str:
    out = []
    for sec, items in LIBRARY:
        cur = ' aria-current="page"'
        links = "".join(
            f'<li><a href="{SLUG[s]}"{cur if s == active else ""}>{html.escape(t)}</a></li>'
            for s, t, _ in items)
        out.append(f'<div class="navsec"><p>{sec}</p><ul>{links}</ul></div>')
    return "".join(out)


def page(title, content, description="", active=None, toc=None, body_class=""):
    tpl = (SITE / "template.html").read_text(encoding="utf-8")
    toc_html = ""
    if toc and len(toc) > 2:
        items = "".join(f'<li><a href="#{i}">{html.escape(n)}</a></li>' for i, n in toc)
        toc_html = f'<nav class="onpage" aria-label="On this page"><p>On this page</p><ol>{items}</ol></nav>'
    return (tpl.replace("{{title}}", html.escape(title))
               .replace("{{description}}", html.escape(description))
               .replace("{{nav}}", nav_html(active) if active is not None else "")
               .replace("{{toc}}", toc_html)
               .replace("{{body_class}}", body_class)
               .replace("{{content}}", content)
               .replace("{{repo}}", REPO_URL))


def scale_svg() -> str:
    """Circle -> Mesh -> Assembly, drawn with one dot per person."""
    import math
    def circle(cx, cy, r, n, dot):
        ring = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="ring"/>'
        dots = "".join(
            f'<circle cx="{cx + r * math.cos(2 * math.pi * k / n - math.pi / 2):.1f}" '
            f'cy="{cy + r * math.sin(2 * math.pi * k / n - math.pi / 2):.1f}" r="{dot}" class="p"/>'
            for k in range(n))
        return ring + dots

    def mesh(cx, cy, cr, gap, dot, hub=True):
        parts = [circle(cx, cy, cr, 5, dot)] if hub else []
        for k in range(6):
            a = 2 * math.pi * k / 6 - math.pi / 2
            parts.append(circle(cx + gap * math.cos(a), cy + gap * math.sin(a), cr, 5, dot))
        return "".join(parts)

    g1 = f'<g class="tier">{circle(137, 120, 46, 5, 7)}</g>'
    g2 = f'<g class="tier">{mesh(410, 120, 20, 50, 3.6)}</g>'
    g3 = '<g class="tier">' + "".join(
        mesh(683 + 64 * math.cos(2 * math.pi * k / 3 - math.pi / 2),
             128 + 64 * math.sin(2 * math.pi * k / 3 - math.pi / 2), 10, 23, 2.6) for k in range(3)) + "</g>"
    arrows = ('<path d="M 200 120 H 325" class="arrow"/><path d="M 495 120 H 595" class="arrow"/>')
    return (f'<svg viewBox="0 0 820 240" class="scale-svg" role="img" aria-labelledby="scaleTitle">'
            f'<title id="scaleTitle">A Circle of 3 to 7 people; up to 7 Circles form a Mesh; up to 3 Meshes form an Assembly of about 147 people.</title>'
            f'{arrows}{g1}{g2}{g3}</svg>')


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(SITE / "style.css", OUT / "style.css")
    for img in (ROOT / "branding").glob("*.jpg"):
        shutil.copy(img, OUT / "assets" / img.name)

    # Document pages, with previous / next links in library order
    for i, (sec, src, title, blurb) in enumerate(PAGES):
        body, toc = render(src)
        prev_ = PAGES[i - 1] if i > 0 else None
        next_ = PAGES[i + 1] if i + 1 < len(PAGES) else None
        pager = '<nav class="pager" aria-label="Previous and next">'
        pager += f'<a class="prev" href="{SLUG[prev_[1]]}"><span>Previous</span>{html.escape(prev_[2])}</a>' if prev_ else "<span></span>"
        pager += f'<a class="next" href="{SLUG[next_[1]]}"><span>Next</span>{html.escape(next_[2])}</a>' if next_ else "<span></span>"
        pager += "</nav>"
        edit = f'<p class="edit"><a href="{REPO_URL}/blob/main/{src}">Suggest a change to this page on GitHub</a></p>'
        content = (f'<article class="doc"><p class="crumb">{sec}</p><h1>{html.escape(title)}</h1>'
                   f'<p class="dek">{html.escape(blurb)}</p>{body}{edit}{pager}</article>')
        (OUT / SLUG[src]).write_text(page(title + " · COGS", content, blurb, active=src, toc=toc, body_class="docpage"),
                                     encoding="utf-8")

    # Home page
    home = (SITE / "home.html").read_text(encoding="utf-8")
    cards = []
    for sec, items in LIBRARY:
        rows = "".join(f'<li><a href="{SLUG[s]}"><b>{html.escape(t)}</b><span>{html.escape(b)}</span></a></li>'
                       for s, t, b in items)
        cards.append(f'<section class="shelf"><h3>{sec}</h3><ul>{rows}</ul></section>')
    home = home.replace("{{library}}", "".join(cards)).replace("{{scale}}", scale_svg())
    for src, slug in SLUG.items():
        home = home.replace("{{" + src + "}}", slug)
    (OUT / "index.html").write_text(
        page("COGS · Circle of Good Samaritans", home,
             "An open-source, non-doctrinal framework for small groups who meet weekly to help each other live better lives.",
             body_class="home"), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(PAGES) + 1} pages into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
