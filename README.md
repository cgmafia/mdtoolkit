# 📄 Markdown Toolkit — `mdtoolkit`

> A powerful CLI toolkit to extract code blocks, export tables, generate styled HTML/PDF, and process entire GitHub repositories — all from your Markdown files.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Author](https://img.shields.io/badge/Author-Anand%20Venkataraman-purple.svg)](mailto:vand3dup@gmail.com)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗂 **Code Extraction** | Extracts all fenced code blocks; named from markdown hint or `code_line<N>.ext` |
| 📊 **Table Export** | Exports Markdown tables to CSV or styled XLSX workbooks |
| 🎨 **Styled HTML** | Generates dark-themed professional HTML with embedded CSS |
| 📄 **PDF Export** | Renders PDF via `wkhtmltopdf` or headless Chrome |
| 🐙 **GitHub Mode** | Clones any public repo, discovers all `.md` files, lets you pick and process |
| 🔍 **File Summary** | Quick stats — headings, code blocks, tables, word count |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/anandvenkataraman/mdtoolkit.git
cd mdtoolkit

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Process a local Markdown file directly
python3 tool.py README.md

# Interactive launcher (local file OR GitHub mode)
python3 tool.py
```

---

## 📋 Menu Options

```
  [1]  🗂  Extract Code Blocks    named from markdown or code_line<N>.ext
  [2]  📊  Export Tables -> CSV   one .csv per table
  [3]  📊  Export Tables -> XLSX  all tables in one styled workbook
  [4]  🎨  Export Styled HTML     dark-themed HTML with embedded CSS
  [5]  📄  Export PDF             via wkhtmltopdf or Chrome headless
  [6]  🚀  Do Everything          run all 5 actions at once
  [7]  🔍  File Summary           headings, code blocks, tables count
```

---

## 🐙 GitHub Mode

When you run `python3 tool.py` without arguments, you get a launch menu with a **GitHub repository** option. Accepts any URL format:

```
https://github.com/owner/repo
https://github.com/owner/repo/tree/develop
https://github.com/owner/repo/tree/feature/my-branch
git@github.com:owner/repo.git
owner/repo
```

The tool will:
1. Clone the repo (depth 1 for speed), with ZIP fallback
2. Scan for all `.md` / `.markdown` files (skipping `node_modules`, `.git`, etc.)
3. Present an interactive picker (README.md always listed first)
4. Process the chosen file — or **all files** at once
5. Cache the clone and offer to reuse it on repeat runs

Output is written to:
```
md_toolkit_output/
  github_output/
    owner_repo/
      README/
        code/
        tables/
        README.html
        README.pdf
```

---

## 🗂 Code Block Naming

| Fence in Markdown | Saved As |
|---|---|
| ` ```java:SecurityConfig.java ` | `SecurityConfig.java` |
| ` ```python ` at line 42 | `code_line42.py` |
| ` ```sql ` at line 87 | `code_line87.sql` |

---

## 📦 Dependencies

| Package | Purpose | Required? |
|---|---|---|
| `markdown` | MD → HTML conversion | Recommended |
| `openpyxl` | XLSX table export | For XLSX feature |
| `wkhtmltopdf` | PDF rendering (system tool) | For PDF feature |

Install Python packages:
```bash
pip install markdown openpyxl
```

Install `wkhtmltopdf` (system):
```bash
# Ubuntu / Debian
sudo apt install wkhtmltopdf

# macOS
brew install wkhtmltopdf

# Windows — download installer from:
# https://wkhtmltopdf.org/downloads.html
```

---

## 🖥 Platform Support

| Platform | Status |
|---|---|
| Linux | ✅ Fully supported |
| macOS | ✅ Fully supported |
| Windows | ✅ Works (use `python tool.py` not `python3`) |

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Anand Venkataraman**
- 📧 Email: [vand3dup@gmail.com](mailto:vand3dup@gmail.com)
- 🐙 GitHub: [@anandvenkataraman](https://github.com/anandvenkataraman)

---

## ⭐ Show Your Support

If this tool helped you, please consider giving it a ⭐ on GitHub!
