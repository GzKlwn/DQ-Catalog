#!/usr/bin/env python3
"""DQ-Catalog webapp — browse / filter / download / upload, stdlib only.

Run:
    python webapp/app.py [port]

Opens on http://127.0.0.1:8787 by default. Binds to 127.0.0.1 only — this
tool can push branches and open PRs on the catalog's GitHub repo, so it must
stay local-only, never exposed on the network.
"""
from __future__ import annotations

import io
import json
import mimetypes
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import rule_parser

WEBAPP_DIR = Path(__file__).resolve().parent
REPO_ROOT = WEBAPP_DIR.parent
RULES_DIR = REPO_ROOT / "rules"
METADATA_PATH = REPO_ROOT / "metadata.json"
STATIC_DIR = WEBAPP_DIR / "static"

HOST = "127.0.0.1"
DEFAULT_PORT = 8787

GIT_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# metadata.json + rule file helpers
# ---------------------------------------------------------------------------

def load_metadata() -> dict:
    with open(METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_metadata(meta: dict) -> None:
    with open(METADATA_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")


def upsert_rule_metadata(meta: dict, entry: dict) -> bool:
    """Insert or replace by name. Returns True if it replaced an existing entry."""
    for i, r in enumerate(meta["rules"]):
        if r["name"] == entry["name"]:
            meta["rules"][i] = entry
            return True
    meta["rules"].append(entry)
    return False


def read_rule_markdown(name: str) -> str:
    path = RULES_DIR / name / f"{name}.md"
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_rule_markdown(name: str, text: str) -> None:
    folder = RULES_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / f"{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug or "rule"


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------

def _count_by(rules: list[dict], key: str, is_list: bool) -> list[list]:
    counts: dict[str, int] = {}
    for r in rules:
        vals = r.get(key) or []
        if not is_list:
            vals = [vals] if vals else []
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])


def compute_stats(meta: dict) -> dict:
    rules = meta["rules"]
    return {
        "total": len(rules),
        "totalObjects": len({r.get("object") for r in rules if r.get("object")}),
        "totalTables": len({t for r in rules for t in r.get("tables", [])}),
        "byObject": _count_by(rules, "object", is_list=False),
        "byTable": _count_by(rules, "tables", is_list=True),
        "byDomain": _count_by(rules, "domain", is_list=False),
        "byCriticality": _count_by(rules, "criticality", is_list=False),
        "byIndustry": _count_by(rules, "industries", is_list=True),
    }


# ---------------------------------------------------------------------------
# multipart/form-data (stdlib-only, hand-rolled — browsers use a well-known
# CRLF-delimited boundary format so this is safe without a library)
# ---------------------------------------------------------------------------

def parse_multipart(body: bytes, content_type: str) -> list[dict]:
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not m:
        return []
    boundary = (m.group(1) or m.group(2)).strip()
    delimiter = ("--" + boundary).encode()
    parts = body.split(delimiter)
    files = []
    for part in parts:
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if b"\r\n\r\n" not in part:
            continue
        header_blob, content = part.split(b"\r\n\r\n", 1)
        content = content[:-2] if content.endswith(b"\r\n") else content
        headers = header_blob.decode("utf-8", errors="replace")
        disp = re.search(
            r'Content-Disposition:.*?name="([^"]*)"(?:;\s*filename="([^"]*)")?',
            headers,
            re.IGNORECASE,
        )
        if not disp:
            continue
        files.append({"field": disp.group(1), "filename": disp.group(2), "content": content})
    return files


# ---------------------------------------------------------------------------
# git / gh
# ---------------------------------------------------------------------------

class GitError(RuntimeError):
    pass


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def push_rules_and_open_pr(rule_names: list[str], commit_message: str) -> dict:
    """Branch off main, commit rules/+metadata.json, push, open a PR via gh.
    Always tries to leave the working tree back on main. Returns a dict with
    either {'prUrl': ...} or {'error': ..., 'branch': ...} on partial failure."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    slug = "-".join(slugify(n) for n in rule_names[:3])
    branch = f"catalog-app/add-{slug}-{ts}"[:100]

    with GIT_LOCK:
        try:
            run_git(["checkout", "main"])
            run_git(["pull"])
            run_git(["checkout", "-b", branch])
            run_git(["add", "rules", "metadata.json"])
            run_git(["commit", "-m", commit_message])
            run_git(["push", "-u", "origin", branch])
        except GitError as e:
            # best-effort return to main so the next upload isn't stuck on a branch
            try:
                run_git(["checkout", "main"])
            except GitError:
                pass
            return {"error": str(e), "branch": branch}

        pr_title = commit_message
        pr_body = "Opened automatically by the DQ-Catalog webapp.\n\nRules: " + ", ".join(rule_names)
        pr_result = subprocess.run(
            ["gh", "pr", "create", "--base", "main", "--head", branch,
             "--title", pr_title, "--body", pr_body],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        run_git(["checkout", "main"])

        if pr_result.returncode != 0:
            return {"error": f"gh pr create failed: {pr_result.stderr.strip()}", "branch": branch}

        pr_url = pr_result.stdout.strip().splitlines()[-1] if pr_result.stdout.strip() else ""
        return {"prUrl": pr_url, "branch": branch}


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "DQCatalogWebapp/1.0"

    # -- helpers ------------------------------------------------------------

    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw) if raw else {}

    def _read_raw_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _serve_static(self, rel_path: str) -> None:
        rel_path = rel_path.lstrip("/")
        if rel_path == "" or rel_path == "index.html":
            path = STATIC_DIR / "index.html"
        else:
            path = (STATIC_DIR / rel_path).resolve()
            if STATIC_DIR.resolve() not in path.parents and path != STATIC_DIR.resolve():
                self.send_error(403)
                return
        if not path.is_file():
            self.send_error(404)
            return
        content_type, _ = mimetypes.guess_type(str(path))
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):  # quieter console output
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {fmt % args}\n")

    # -- routing --------------------------------------------------------

    def do_GET(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        try:
            if path == "/api/rules":
                return self._send_json(200, load_metadata()["rules"])

            if path == "/api/stats":
                return self._send_json(200, compute_stats(load_metadata()))

            m = re.fullmatch(r"/api/rules/([^/]+)/download", path)
            if m:
                return self._handle_download(m.group(1), query)

            m = re.fullmatch(r"/api/rules/([^/]+)", path)
            if m:
                return self._handle_detail(m.group(1))

            if path.startswith("/api/"):
                return self._send_error_json(404, "unknown API route")

            if path.startswith("/static/"):
                return self._serve_static(path[len("/static/") :])

            return self._serve_static("index.html")
        except Exception as e:  # noqa: BLE001 — surface to the browser, don't 500 blank
            return self._send_error_json(500, str(e))

    def do_POST(self) -> None:
        try:
            if self.path == "/api/upload/parse":
                return self._handle_upload_parse()
            if self.path == "/api/upload/confirm":
                return self._handle_upload_confirm()
            if self.path == "/api/rules/download-zip":
                return self._handle_download_zip()
            return self._send_error_json(404, "unknown API route")
        except Exception as e:  # noqa: BLE001
            return self._send_error_json(500, str(e))

    # -- route implementations ------------------------------------------

    def _handle_detail(self, name: str) -> None:
        try:
            text = read_rule_markdown(name)
        except FileNotFoundError:
            return self._send_error_json(404, f"rule '{name}' not found")
        detail = rule_parser.parse(text)
        meta_entry = next((r for r in load_metadata()["rules"] if r["name"] == name), {})
        detail["name"] = name
        detail["object"] = meta_entry.get("object", "")
        detail["industries"] = meta_entry.get("industries", [])
        self._send_json(200, detail)

    def _handle_download(self, name: str, query: dict) -> None:
        system_id = (query.get("system_id") or [""])[0].strip()
        if not system_id:
            return self._send_error_json(400, "system_id query parameter is required")
        try:
            text = read_rule_markdown(name)
        except FileNotFoundError:
            return self._send_error_json(404, f"rule '{name}' not found")
        adapted = rule_parser.substitute_source_system(text, system_id)
        data = adapted.encode("utf-8")
        filename = f"{name}_{slugify(system_id)}.md"
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_download_zip(self) -> None:
        payload = self._read_json_body()
        names = payload.get("names") or []
        system_id = (payload.get("system_id") or "").strip()
        if not names:
            return self._send_error_json(400, "names must be a non-empty list")
        if not system_id:
            return self._send_error_json(400, "system_id is required")

        buf = io.BytesIO()
        included, missing = [], []
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in names:
                try:
                    text = read_rule_markdown(name)
                except FileNotFoundError:
                    missing.append(name)
                    continue
                adapted = rule_parser.substitute_source_system(text, system_id)
                zf.writestr(f"{name}_{slugify(system_id)}.md", adapted)
                included.append(name)

        if not included:
            return self._send_error_json(404, f"none of the requested rules were found: {', '.join(missing)}")

        data = buf.getvalue()
        filename = f"dq-catalog-rules_{slugify(system_id)}.zip"
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        if missing:
            # Surface partial-success info without failing the whole download —
            # the browser can't read a custom header on a file-save navigation,
            # but curl/fetch-based callers (and the console) can see it.
            self.send_header("X-Missing-Rules", ", ".join(missing))
        self.end_headers()
        self.wfile.write(data)

    def _handle_upload_parse(self) -> None:
        content_type = self.headers.get("Content-Type", "")
        body = self._read_raw_body()
        files = [f for f in parse_multipart(body, content_type) if f.get("filename")]
        if not files:
            return self._send_error_json(400, "no .md files found in upload")

        previews = []
        for f in files:
            try:
                text = f["content"].decode("utf-8")
            except UnicodeDecodeError:
                previews.append({"filename": f["filename"], "error": "not valid UTF-8 text"})
                continue
            # Normalize to LF — every existing rule .md in this repo is LF-only;
            # keep uploads consistent regardless of the contributor's OS/editor.
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            parsed = rule_parser.parse(text)
            name = slugify(Path(f["filename"]).stem)
            previews.append(
                {
                    "name": name,
                    "filename": f["filename"],
                    "markdown": text,
                    "metadata": {
                        "name": name,
                        "object": "",
                        "dataType": parsed["dataType"],
                        "description": parsed["description"],
                        "tables": parsed["tables"],
                        "fields": parsed["fields"],
                        "criticality": parsed["criticality"],
                        "industries": [],
                        "domain": parsed["domain"],
                    },
                    "existsAlready": (RULES_DIR / name / f"{name}.md").exists(),
                }
            )
        self._send_json(200, {"rules": previews})

    def _handle_upload_confirm(self) -> None:
        payload = self._read_json_body()
        rules = payload.get("rules", [])
        if not rules:
            return self._send_error_json(400, "no rules provided")

        meta = load_metadata()
        names = []
        for r in rules:
            name = slugify(r["metadata"]["name"])
            names.append(name)
            write_rule_markdown(name, r["markdown"])
            entry = dict(r["metadata"])
            entry["name"] = name
            upsert_rule_metadata(meta, entry)
        save_metadata(meta)

        verb = "Update" if len(names) == 1 else "Add"
        commit_message = f"feat: {verb} rule(s) via Catalog webapp: {', '.join(names)}"
        result = push_rules_and_open_pr(names, commit_message)

        if "error" in result:
            return self._send_json(207, {"names": names, **result})
        self._send_json(200, {"names": names, **result})


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = ThreadingHTTPServer((HOST, port), Handler)
    print(f"DQ-Catalog webapp: http://{HOST}:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
