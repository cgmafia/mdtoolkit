"""
Code block extraction from Markdown files.

Naming rules
------------
- Explicit hint  ```java:MyClass.java   → MyClass.java
- No hint        ```python at line 42   → code_line42.py
"""

import re
from pathlib import Path
from mdtoolkit.colors import ok, warn, G, W, C, DIM, RST

EXT_MAP: dict = {
    "python": "py",    "py": "py",        "java": "java",
    "javascript": "js","js": "js",        "typescript": "ts",  "ts": "ts",
    "sql": "sql",      "bash": "sh",      "shell": "sh",       "sh": "sh",
    "html": "html",    "css": "css",      "xml": "xml",
    "yaml": "yml",     "yml": "yml",      "json": "json",
    "kotlin": "kt",    "go": "go",        "cpp": "cpp",        "c": "c",
    "ruby": "rb",      "rust": "rs",      "php": "php",
    "swift": "swift",  "scala": "scala",  "r": "r",
    "markdown": "md",  "md": "md",        "dockerfile": "dockerfile",
}


def extract_code_blocks(md_text: str) -> list:
    """
    Parse all fenced code blocks in *md_text*.

    Returns a list of tuples:
        (lang: str, hint: str, code: str, line_no: int)

    *line_no* is the 1-based line number of the opening ``` fence.
    Used as the fallback filename:  code_line<N>.<ext>
    """
    fence_re = re.compile(
        r"```[ \t]*([a-zA-Z0-9_+#.-]*)(?::([^\n]+))?\n(.*?)```",
        re.DOTALL,
    )

    # Build char-offset → 1-based line number index
    line_starts = [0]
    for i, ch in enumerate(md_text):
        if ch == "\n":
            line_starts.append(i + 1)

    def offset_to_line(offset: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1  # 1-based

    result = []
    for m in fence_re.finditer(md_text):
        lang    = m.group(1).strip() if m.group(1) else ""
        hint    = m.group(2).strip() if m.group(2) else ""
        code    = m.group(3)
        line_no = offset_to_line(m.start())
        result.append((lang, hint, code, line_no))
    return result


def save_code_files(md_path: Path, md_text: str, out_dir: Path) -> None:
    """Extract all code blocks and save them as individual files."""
    blocks = extract_code_blocks(md_text)
    if not blocks:
        warn("No fenced code blocks found.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    for lang, hint, code, line_no in blocks:
        ext   = EXT_MAP.get(lang.lower(), "txt") if lang else "txt"
        fname = hint.replace("/", "_") if hint else ("code_line" + str(line_no) + "." + ext)
        dest  = out_dir / fname

        # Deduplicate
        stem, sfx = dest.stem, dest.suffix
        dup = 1
        while dest.exists():
            dest = out_dir / (stem + "_" + str(dup) + sfx)
            dup += 1

        dest.write_text(code, encoding="utf-8")
        saved.append((dest.name, lang or "—", line_no, len(code.splitlines())))

    # Results table
    print()
    print("  " + G + "FILE".ljust(35) + "LANG".ljust(16) + "LINE".rjust(5) + "  LINES" + RST)
    print("  " + "─" * 64)
    for fname, lang, lno, cnt in saved:
        print("  " + W + fname.ljust(35) + RST +
              C + lang.ljust(16) + RST +
              DIM + str(lno).rjust(5) + RST + "  " + str(cnt))
    print()
    ok(str(len(saved)) + " file(s) saved to  " + str(out_dir) + "/")
