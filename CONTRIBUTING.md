# Contributing to Markdown Toolkit

Thank you for considering contributing! Every improvement — big or small — is appreciated.

## How to Contribute

### Reporting Bugs
- Open an issue at [GitHub Issues](https://github.com/anandvenkataraman/mdtoolkit/issues)
- Include your OS, Python version, and the full error message
- Attach the Markdown file that caused the issue if possible

### Suggesting Features
- Open an issue with the label `enhancement`
- Describe the use case clearly — why would this help others?

### Submitting Code

1. **Fork** the repository and clone your fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/mdtoolkit.git
   cd mdtoolkit
   ```

2. **Create a branch** — name it descriptively
   ```bash
   git checkout -b feature/add-docx-export
   # or
   git checkout -b fix/table-parser-empty-cells
   ```

3. **Make your changes** — keep commits small and focused

4. **Test your changes**
   ```bash
   # Run the smoke test
   python3 tool.py demo.md
   # Choose option 6 (Do Everything) and verify outputs
   ```

5. **Push and open a Pull Request**
   ```bash
   git push origin feature/add-docx-export
   ```
   Then open a PR on GitHub — describe what changed and why.

## Code Style

- Python 3.8+ compatible (no walrus operator, no match statements)
- No external dependencies beyond `requirements.txt`
- Keep the single-file design of `tool.py` — it makes the tool easy to share
- Use the existing ANSI helpers (`ok()`, `err()`, `info()`, etc.) for all output
- New features should include a menu entry and integrate with option `[6] Do Everything`

## Ideas for Contributions

- [ ] DOCX export support
- [ ] Syntax highlighting in HTML output
- [ ] Support for private GitHub repos (token auth)
- [ ] GitLab / Bitbucket URL support
- [ ] `--batch` CLI flag to process multiple files non-interactively
- [ ] Table of contents generation as a standalone feature

## License

By contributing, you agree your contributions will be licensed under the MIT License.
