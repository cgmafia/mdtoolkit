"""
Entry point for:
  python -m mdtoolkit [file.md]
  mdtoolkit [file.md]          ← after pip install
"""

import sys
from pathlib import Path

from mdtoolkit import __version__
from mdtoolkit.colors   import banner, info, ok, warn, err, head, B, W, G, DIM, RST
from mdtoolkit.extractor import extract_code_blocks, save_code_files, EXT_MAP
from mdtoolkit.tables    import extract_tables, export_tables
from mdtoolkit.renderer  import build_html, save_html, export_pdf
from mdtoolkit.github    import github_flow
import re


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_md(path: Path) -> str:
    if not path.exists():
        err("File not found: " + str(path))
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def print_usage() -> None:
    print("Usage: mdtoolkit [file.md] [options]")
    print()
    print("  Process a local Markdown file, or launch the interactive")
    print("  menu when called with no arguments.")
    print()
    print("Options:")
    print("  -h, --help     Show this help message and exit")
    print("  -v, --version  Show version and exit")


def file_summary(md_path: Path, md_text: str) -> None:
    head("📋  Summary of  " + md_path.name)
    lines  = md_text.splitlines()
    blocks = extract_code_blocks(md_text)
    tables = extract_tables(md_text)
    links  = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", md_text)

    info("Total lines  : " + str(len(lines)))
    info("Words        : " + str(len(md_text.split())))
    info("H1 headings  : " + str(sum(1 for l in lines if l.startswith("# "))))
    info("H2 headings  : " + str(sum(1 for l in lines if l.startswith("## "))))
    info("H3 headings  : " + str(sum(1 for l in lines if l.startswith("### "))))
    info("Code blocks  : " + str(len(blocks)))
    info("Tables       : " + str(len(tables)))
    info("Links        : " + str(len(links)))

    if blocks:
        head("Code blocks")
        for i, (lang, hint, code, line_no) in enumerate(blocks, 1):
            ext   = EXT_MAP.get(lang.lower(), "txt") if lang else "txt"
            label = hint if hint else "(→ code_line" + str(line_no) + "." + ext + ")"
            print("  " + DIM + "#" + str(i).ljust(3) +
                  " line=" + str(line_no).ljust(5) +
                  " lang=" + (lang or "none").ljust(12) +
                  "  " + label + RST)

    if tables:
        head("Tables")
        for i, tbl in enumerate(tables, 1):
            print("  " + DIM + "#" + str(i) + "  " +
                  str(len(tbl[0])) + " cols x " + str(len(tbl)) +
                  " rows  |  header: " + ", ".join(tbl[0]) + RST)


# ── Per-file menu ─────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1", "🗂  Extract Code Blocks",   "named from markdown or code_line<N>.ext"),
    ("2", "📊  Export Tables -> CSV",  "one .csv per table"),
    ("3", "📊  Export Tables -> XLSX", "all tables in one styled workbook"),
    ("4", "🎨  Export Styled HTML",    "dark-themed HTML with embedded CSS"),
    ("5", "📄  Export PDF",            "via wkhtmltopdf or Chrome headless"),
    ("6", "🚀  Do Everything",         "run all 5 actions at once"),
    ("7", "🔍  File Summary",          "headings, code blocks, tables count"),
    ("Q", "🚪  Quit / Back",           ""),
]


def print_file_menu() -> None:
    print("\n" + W + "  ┌─ What would you like to do? ─────────────────────────┐" + RST)
    for key, label, hint in MENU_ITEMS:
        hint_str = ("  " + DIM + hint + RST) if hint else ""
        print("  " + B + "[" + key + "]" + RST + "  " + label + hint_str)
    print(W + "  └──────────────────────────────────────────────────────────┘" + RST)


def run_menu(md_path: Path, out_dir: Path, single_shot: bool = False) -> None:
    """
    Interactive per-file action menu.
    single_shot=True → execute 'Do Everything' once and return (batch mode).
    """
    md_text = load_md(md_path)

    if not single_shot:
        info("File  :  " + str(md_path))
        info("Output:  " + str(out_dir) + "/")

    while True:
        if single_shot:
            choice = "6"
        else:
            print_file_menu()
            choice = input("\n  " + W + "Enter choice: " + RST).strip().upper()

        if choice == "1":
            head("📂  Extracting Code")
            save_code_files(md_path, md_text, out_dir / "code")
        elif choice == "2":
            head("📊  Exporting Tables -> CSV")
            export_tables(md_path, md_text, "csv", out_dir / "tables")
        elif choice == "3":
            head("📊  Exporting Tables -> XLSX")
            export_tables(md_path, md_text, "xlsx", out_dir / "tables")
        elif choice == "4":
            head("🎨  Exporting Styled HTML")
            ok("HTML saved  ->  " + str(save_html(md_path, md_text, out_dir)))
        elif choice == "5":
            head("📄  Exporting PDF")
            export_pdf(md_path, md_text, out_dir)
        elif choice == "6":
            head("🚀  Running All Actions")
            save_code_files(md_path, md_text, out_dir / "code")
            export_tables(md_path, md_text, "csv",  out_dir / "tables")
            export_tables(md_path, md_text, "xlsx", out_dir / "tables")
            ok("HTML  ->  " + str(save_html(md_path, md_text, out_dir)))
            export_pdf(md_path, md_text, out_dir)
            ok("All done!")
            if single_shot:
                return
        elif choice == "7":
            file_summary(md_path, md_text)
        elif choice in ("Q", "QUIT", "EXIT", "0", "B", "BACK"):
            return
        else:
            warn("Invalid choice. Please try again.")


# ── Launch menu ───────────────────────────────────────────────────────────────

LAUNCH_ITEMS = [
    ("1", "📂  Open local Markdown file", "pass a path or enter it now"),
    ("2", "🐙  GitHub repository",        "clone & pick a Markdown file"),
    ("Q", "🚪  Quit",                     ""),
]


def print_launch_menu() -> None:
    print("\n" + W + "  ┌─ Choose mode ────────────────────────────────────────────┐" + RST)
    for key, label, hint in LAUNCH_ITEMS:
        hint_str = ("  " + DIM + hint + RST) if hint else ""
        print("  " + B + "[" + key + "]" + RST + "  " + label + hint_str)
    print(W + "  └───────────────────────────────────────────────────────────┘" + RST)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    """Console-script entry point: `mdtoolkit [file.md]`"""
    banner(__version__)

    # Direct file argument
    if len(sys.argv) >= 2:
        if sys.argv[1] in ("-v", "--version"):
            print("mdtoolkit v" + __version__)
            sys.exit(0)
        if sys.argv[1] in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        md_path = Path(sys.argv[1]).resolve()
        out_dir = md_path.parent / (md_path.stem + "_output")
        run_menu(md_path, out_dir)
        sys.exit(0)

    # Interactive launcher
    base_out = Path.cwd() / "md_toolkit_output"
    base_out.mkdir(parents=True, exist_ok=True)

    while True:
        print_launch_menu()
        choice = input("\n  " + W + "Enter choice: " + RST).strip().upper()

        if choice == "1":
            raw = input("  " + W + "Path to Markdown file: " + RST).strip()
            if not raw:
                warn("No path entered.")
                continue
            md_path = Path(raw).expanduser().resolve()
            if not md_path.exists():
                err("File not found: " + str(md_path))
                continue
            out_dir = base_out / md_path.stem
            run_menu(md_path, out_dir)

        elif choice == "2":
            github_flow(base_out, run_menu)

        elif choice in ("Q", "QUIT", "EXIT", "0"):
            print("\n  " + G + "Goodbye! ✨" + RST + "\n")
            break
        else:
            warn("Invalid choice.")


if __name__ == "__main__":
    main()
