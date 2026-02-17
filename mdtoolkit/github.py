"""
GitHub repository download, Markdown file discovery, and interactive picker.
"""

import re
import shutil
import zipfile
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

from mdtoolkit.colors import ok, warn, err, info, head, dim, step, B, W, Y, DIM, RST


def parse_github_url(raw: str):
    """
    Accept any GitHub URL format and return (owner, repo, branch_hint).

    Supported formats
    -----------------
    https://github.com/owner/repo
    https://github.com/owner/repo.git
    https://github.com/owner/repo/tree/branch
    https://github.com/owner/repo/tree/feature/my-branch
    git@github.com:owner/repo.git
    owner/repo  (shorthand)
    """
    raw = raw.strip().rstrip("/")

    # SSH
    ssh = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", raw)
    if ssh:
        return ssh.group(1), ssh.group(2), None

    # HTTPS with optional /tree/<branch>  (branch may contain slashes)
    https = re.match(
        r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/tree/(.+))?$",
        raw,
    )
    if https:
        return https.group(1), https.group(2), https.group(3)

    # Shorthand  owner/repo
    short = re.match(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$", raw)
    if short:
        return short.group(1), short.group(2), None

    return None, None, None


def clone_with_git(clone_url: str, dest: Path, branch: str = None) -> bool:
    """Shallow-clone a repository. Returns True on success."""
    cmd = ["git", "clone", "--depth", "1", "--quiet"]
    if branch:
        cmd += ["--branch", branch]
    cmd += [clone_url, str(dest)]
    step("git clone " + clone_url + (" @ " + branch if branch else ""))
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode == 0:
        ok("Clone complete")
        return True
    err("git clone failed: " + r.stderr.decode()[:300].strip())
    return False


def download_zip(owner: str, repo: str, branch: str, dest: Path) -> bool:
    """
    Download GitHub ZIP archive; tries main → master → HEAD if branch is None.
    Returns True on success.
    """
    branches_to_try = [branch] if branch else ["main", "master", "HEAD"]
    for br in branches_to_try:
        if br == "HEAD":
            url = "https://github.com/" + owner + "/" + repo + "/archive/HEAD.zip"
        else:
            url = "https://github.com/" + owner + "/" + repo + "/archive/refs/heads/" + br + ".zip"
        step("Trying ZIP: " + url)
        try:
            tmp_zip = dest.parent / (repo + "_" + br + ".zip")
            urllib.request.urlretrieve(url, str(tmp_zip))
            with zipfile.ZipFile(str(tmp_zip), "r") as zf:
                zf.extractall(str(dest.parent))
            tmp_zip.unlink()
            extracted = dest.parent / (repo + "-" + br)
            if extracted.exists():
                if dest.exists():
                    shutil.rmtree(dest)
                extracted.rename(dest)
            ok("ZIP download complete (" + br + " branch)")
            return True
        except urllib.error.HTTPError as e:
            warn("HTTP " + str(e.code) + " for branch '" + br + "' — trying next")
        except Exception as e:
            warn("ZIP error: " + str(e))
    return False


def _do_download(owner: str, repo: str, branch: str, dest: Path) -> bool:
    """Try git clone first, fall back to ZIP."""
    clone_url = "https://github.com/" + owner + "/" + repo + ".git"
    if clone_with_git(clone_url, dest, branch):
        return True
    warn("git clone failed — trying ZIP download …")
    if download_zip(owner, repo, branch, dest):
        return True
    err("Could not download repository.")
    info("Check the URL, network connection, and that the repo is public.")
    return False


def find_md_files(root: Path) -> list:
    """
    Recursively find .md / .markdown files under *root*.
    Skips hidden dirs and common non-source directories.
    Returns sorted list with README.md first.
    """
    skip_dirs = {
        ".git", ".github", "node_modules", "vendor", ".tox",
        "__pycache__", "venv", ".venv", "dist", "build",
    }
    found = []
    for p in root.rglob("*"):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.suffix.lower() in (".md", ".markdown") and p.is_file():
            found.append(p)

    def sort_key(p):
        rel = p.relative_to(root)
        return (0 if p.stem.lower() == "readme" else 1, str(rel).lower())

    return sorted(found, key=sort_key)


def pick_md_file(md_files: list, repo_root: Path):
    """
    Interactive numbered picker.
    Returns a Path, "ALL", or None to cancel.
    """
    if not md_files:
        err("No Markdown files found in this repository.")
        return None

    if len(md_files) == 1:
        info("Single Markdown file found: " + str(md_files[0].relative_to(repo_root)))
        return md_files[0]

    head("📑  Markdown files in repository")
    for i, p in enumerate(md_files, 1):
        rel      = p.relative_to(repo_root)
        size     = p.stat().st_size
        size_str = (str(size // 1024) + " KB") if size >= 1024 else (str(size) + " B")
        print("  " + B + "[" + str(i).rjust(2) + "]" + RST +
              "  " + W + str(rel) + RST +
              "  " + DIM + size_str + RST)
    print("  " + B + "[ A]" + RST + "  " + Y + "Process ALL files" + RST)
    print("  " + B + "[ 0]" + RST + "  " + DIM + "Cancel / go back" + RST)

    while True:
        raw = input("\n  " + W + "Choose file (number / A / 0): " + RST).strip().upper()
        if raw == "0":
            return None
        if raw == "A":
            return "ALL"
        try:
            idx = int(raw)
            if 1 <= idx <= len(md_files):
                return md_files[idx - 1]
            warn("Enter a number between 1 and " + str(len(md_files)))
        except ValueError:
            warn("Invalid input.")


def github_flow(base_out_dir: Path, run_menu_fn) -> None:
    """
    Full GitHub → clone → pick MD → process flow.

    Parameters
    ----------
    base_out_dir : Path   root output directory
    run_menu_fn  : callable(md_path, out_dir, single_shot)
    """
    head("🐙  GitHub Repository Mode")
    print()
    print("  " + DIM + "Examples:" + RST)
    print("  " + DIM + "  https://github.com/owner/repo" + RST)
    print("  " + DIM + "  https://github.com/owner/repo/tree/develop" + RST)
    print("  " + DIM + "  git@github.com:owner/repo.git" + RST)
    print("  " + DIM + "  owner/repo" + RST)
    print()

    raw_url = input("  " + W + "GitHub URL or shorthand: " + RST).strip()
    if not raw_url:
        warn("No URL entered — returning to menu.")
        return

    owner, repo, branch_hint = parse_github_url(raw_url)
    if not owner:
        err("Could not parse GitHub URL: " + raw_url)
        return

    info("Owner  : " + owner)
    info("Repo   : " + repo)
    info("Branch : " + (branch_hint or "(auto-detect)"))

    if not branch_hint:
        override = input(
            "\n  " + DIM + "Branch name (leave blank for default main/master): " + RST
        ).strip()
        if override:
            branch_hint = override

    clone_dir = base_out_dir / "repos" / (owner + "_" + repo)

    if clone_dir.exists():
        print()
        warn("Local copy already exists: " + str(clone_dir))
        reuse = input("  " + W + "Use cached copy? [Y/n]: " + RST).strip().lower()
        if reuse in ("n", "no"):
            step("Removing old copy …")
            shutil.rmtree(clone_dir)
            clone_dir.mkdir(parents=True, exist_ok=True)
            if not _do_download(owner, repo, branch_hint, clone_dir):
                shutil.rmtree(clone_dir, ignore_errors=True)
                return
        else:
            info("Reusing cached repository.")
    else:
        clone_dir.mkdir(parents=True, exist_ok=True)
        if not _do_download(owner, repo, branch_hint, clone_dir):
            shutil.rmtree(clone_dir, ignore_errors=True)
            return

    step("Scanning for Markdown files …")
    md_files = find_md_files(clone_dir)
    info("Found " + str(len(md_files)) + " Markdown file(s)")

    while True:
        choice = pick_md_file(md_files, clone_dir)
        if choice is None:
            info("Cancelled — returning to main menu.")
            return

        if choice == "ALL":
            for md_path in md_files:
                out_dir = (base_out_dir / "github_output" /
                           (owner + "_" + repo) / md_path.stem)
                print()
                info("Processing: " + str(md_path.relative_to(clone_dir)))
                run_menu_fn(md_path, out_dir, single_shot=True)
            info("All files processed.")
            return
        else:
            out_dir = (base_out_dir / "github_output" /
                       (owner + "_" + repo) / choice.stem)
            run_menu_fn(choice, out_dir)
            print()
            again = input(
                "  " + W + "Process another file from this repo? [y/N]: " + RST
            ).strip().lower()
            if again not in ("y", "yes"):
                return
