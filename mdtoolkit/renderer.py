"""
Styled HTML generation and PDF export.
"""

import re
import subprocess
from pathlib import Path
from mdtoolkit.colors import ok, warn, err, info

CSS = """
:root{--bg:#0f172a;--surface:#1e293b;--border:#334155;--accent:#3b82f6;
  --accent2:#8b5cf6;--text:#e2e8f0;--muted:#94a3b8;--code-bg:#020617;
  --link:#60a5fa;--font:'Segoe UI',system-ui,sans-serif;
  --mono:'JetBrains Mono','Fira Code',monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--font);
  font-size:16px;line-height:1.75}
.md-container{max-width:900px;margin:0 auto;padding:60px 40px}
h1,h2,h3,h4,h5,h6{font-weight:700;line-height:1.3;margin:2em 0 .6em;letter-spacing:-.02em}
h1{font-size:2.4em;background:linear-gradient(135deg,#60a5fa,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;border-bottom:2px solid var(--border);padding-bottom:.4em}
h2{font-size:1.7em;color:#93c5fd;border-bottom:1px solid var(--border);padding-bottom:.3em}
h3{font-size:1.3em;color:#a5b4fc}
h4{font-size:1.1em;color:#c4b5fd}
p{margin:.9em 0}
a{color:var(--link);text-decoration:none;border-bottom:1px solid #3b82f640}
a:hover{color:#93c5fd;border-color:#93c5fd}
code{font-family:var(--mono);font-size:.85em;background:var(--code-bg);color:#f472b6;
  padding:2px 6px;border-radius:4px;border:1px solid var(--border)}
pre{background:var(--code-bg);border:1px solid var(--border);
  border-left:4px solid var(--accent);border-radius:8px;
  padding:1.2em 1.5em;overflow-x:auto;margin:1.5em 0;position:relative}
pre code{background:transparent;color:var(--text);border:none;padding:0;
  font-size:.88em;line-height:1.6}
pre::before{content:attr(data-lang);position:absolute;top:8px;right:14px;
  font-size:.72em;color:var(--muted);text-transform:uppercase;
  letter-spacing:.08em;font-family:var(--font)}
table{width:100%;border-collapse:collapse;margin:1.8em 0;
  border-radius:8px;overflow:hidden;box-shadow:0 0 0 1px var(--border)}
thead tr{background:linear-gradient(135deg,#1e3a5f,#2d1f6e)}
th{color:#e2e8f0;font-weight:600;font-size:.85em;text-transform:uppercase;
  letter-spacing:.06em;padding:12px 16px;text-align:left}
td{padding:11px 16px;border-top:1px solid var(--border);font-size:.94em}
tbody tr:nth-child(even){background:#162032}
tbody tr:hover{background:#1a2840}
blockquote{border-left:4px solid var(--accent2);background:#1e1b4b40;
  padding:.8em 1.2em;border-radius:0 8px 8px 0;margin:1.5em 0;
  color:var(--muted);font-style:italic}
ul,ol{padding-left:1.6em;margin:.8em 0}
li{margin:.35em 0}
ul li::marker{color:var(--accent)}
ol li::marker{color:var(--accent2);font-weight:700}
hr{border:none;border-top:1px solid var(--border);margin:2.5em 0}
strong{color:#f8fafc;font-weight:700}
em{color:#c4b5fd}
"""


def build_html(md_path: Path, md_text: str) -> str:
    """Convert Markdown to a fully self-contained styled HTML string."""
    try:
        import markdown as md_lib
        html_body = md_lib.markdown(
            md_text,
            extensions=["fenced_code", "tables", "toc", "attr_list", "nl2br"],
        )
    except ImportError:
        html_body = _minimal_md_to_html(md_text)

    def tag_pre(m):
        cls  = m.group(1)
        body = m.group(2)
        lang = re.search(r'class="language-(\w+)"', cls)
        dl   = ' data-lang="' + lang.group(1) + '"' if lang else ""
        return "<pre" + dl + "><code " + cls + ">" + body + "</code></pre>"

    html_body = re.sub(r'<pre><code ([^>]*)>(.*?)</code></pre>',
                       tag_pre, html_body, flags=re.DOTALL)

    title = md_path.stem.replace("_", " ").replace("-", " ").title()
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '  <meta charset="UTF-8"/>\n'
        '  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>\n'
        '  <title>' + title + '</title>\n'
        '  <style>\n' + CSS + '\n  </style>\n</head>\n<body>\n'
        '  <div class="md-container">\n' + html_body + '\n  </div>\n</body>\n</html>\n'
    )


def _minimal_md_to_html(text: str) -> str:
    """Fallback converter when the `markdown` package is not installed."""
    t = text
    t = re.sub(r"^# (.+)$",   r"<h1>\1</h1>", t, flags=re.M)
    t = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", t, flags=re.M)
    t = re.sub(r"^### (.+)$", r"<h3>\1</h3>", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*",     r"<em>\1</em>",         t)
    t = re.sub(r"`(.+?)`",       r"<code>\1</code>",      t)
    t = re.sub(r"```.*?\n(.*?)```", r"<pre><code>\1</code></pre>", t, flags=re.DOTALL)
    return "\n".join(
        ("<p>" + l + "</p>" if not re.match(r"^<", l.strip()) and l.strip() else l)
        for l in t.splitlines()
    )


def save_html(md_path: Path, md_text: str, out_dir: Path) -> Path:
    """Write styled HTML to *out_dir* and return the output path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / (md_path.stem + ".html")
    dest.write_text(build_html(md_path, md_text), encoding="utf-8")
    return dest


def export_pdf(md_path: Path, md_text: str, out_dir: Path) -> None:
    """Render PDF using wkhtmltopdf (primary) or headless Chrome (fallback)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = save_html(md_path, md_text, out_dir)
    pdf_path  = out_dir / (md_path.stem + ".pdf")

    if subprocess.run(["which", "wkhtmltopdf"], capture_output=True).returncode == 0:
        r = subprocess.run(
            ["wkhtmltopdf", "--page-size", "A4",
             "--margin-top", "15mm", "--margin-bottom", "15mm",
             "--margin-left", "12mm", "--margin-right", "12mm",
             "--enable-local-file-access", "--quiet",
             str(html_path), str(pdf_path)],
            capture_output=True,
        )
        if r.returncode == 0:
            ok("PDF saved  →  " + str(pdf_path))
            return
        warn("wkhtmltopdf: " + r.stderr.decode()[:200])

    for browser in ("google-chrome", "chromium-browser", "chromium"):
        if subprocess.run(["which", browser], capture_output=True).returncode == 0:
            r = subprocess.run(
                [browser, "--headless", "--disable-gpu", "--no-sandbox",
                 "--print-to-pdf=" + str(pdf_path), str(html_path)],
                capture_output=True,
            )
            if r.returncode == 0:
                ok("PDF saved  →  " + str(pdf_path))
                return
            warn(browser + ": " + r.stderr.decode()[:200])

    err("No PDF renderer found (wkhtmltopdf or Chrome/Chromium required).")
    info("HTML exported instead → " + str(html_path))
