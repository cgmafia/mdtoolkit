# Changelog

All notable changes to **Markdown Toolkit** will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-02-17

### Added
- 🗂 **Code extraction** — extracts all fenced code blocks to individual files
  - Named from markdown hint (` ```java:MyClass.java `)
  - Falls back to `code_line<N>.ext` using actual source line number
- 📊 **Table export** — exports Markdown tables to CSV or styled XLSX
- 🎨 **Styled HTML** — dark-themed professional HTML with embedded CSS
- 📄 **PDF export** — via `wkhtmltopdf` with headless Chrome fallback
- 🐙 **GitHub mode** — clone any public repo and process its Markdown files
  - Supports HTTPS, SSH, shorthand `owner/repo`, and `/tree/<branch>` URLs
  - Handles slash-containing branch names (e.g. `feature/my-branch`)
  - ZIP download fallback when `git` is unavailable
  - Smart clone cache with reuse prompt
  - Recursive Markdown file scanner (skips `.git`, `node_modules`, etc.)
  - Interactive file picker with README.md prioritised first
  - Batch mode to process ALL files in one shot
- 🔍 **File summary** — quick stats per file
- 🚀 **Do Everything** mode — runs all 5 actions at once
- Interactive CLI launcher with coloured ANSI interface

### Author
- Anand Venkataraman (vand3dup@gmail.com)
