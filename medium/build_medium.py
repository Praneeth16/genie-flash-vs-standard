"""Build medium/final.md and medium/chunks.json from article/draft.md.
chunks.json is a list of {"html": ...} and {"image": path, "alt": ...} items in order,
used to paste text and upload images into the Medium editor."""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "article/draft.md").read_text()

# Medium has its own title and byline, so drop the H1 and the byline line.
lines = md.splitlines()
assert lines[0].startswith("# ")
body = "\n".join(l for l in lines[1:] if not l.startswith("Praneeth Paikray, "))

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', t)
    return t

chunks, buf = [], []
def flush():
    if buf:
        chunks.append({"html": "".join(buf)})
        buf.clear()

blocks = re.split(r"\n\s*\n", body.strip())
for b in blocks:
    b = b.strip()
    m = re.fullmatch(r"!\[(.+?)\]\((.+?)\)", b, re.S)
    if m:
        flush()
        chunks.append({"image": str((ROOT / "article" / m.group(2)).resolve().relative_to(ROOT)), "alt": m.group(1)})
    elif b.startswith("## "):
        buf.append(f"<h3>{inline(b[3:])}</h3>")
    elif all(l.startswith("- ") for l in b.splitlines()):
        buf.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in b.splitlines()) + "</ul>")
    elif b.startswith("> "):
        buf.append(f"<blockquote>{inline(b[2:])}</blockquote>")
    elif all(re.match(r"\d+\. ", l) for l in b.splitlines()):
        buf.append("<ol>" + "".join(f"<li>{inline(re.sub(r'^\d+\. ', '', l))}</li>" for l in b.splitlines()) + "</ol>")
    else:
        buf.append(f"<p>{inline(' '.join(b.splitlines()))}</p>")
flush()

for c in chunks:
    if "image" in c:
        assert (ROOT / c["image"]).exists(), c["image"]
(ROOT / "medium/chunks.json").write_text(json.dumps(chunks, indent=1))

final = re.sub(r"!\[(.+?)\]\(\.\./(.+?)\)", lambda m: f"[IMAGE: {m.group(2)}]\nAlt text: {m.group(1)}", md)
(ROOT / "medium/final.md").write_text(final)
prose = re.sub(r"!\[.*?\]\(.*?\)", "", md)
print("chunks", len(chunks), "images", sum("image" in c for c in chunks), "prose words", len(prose.split()))
