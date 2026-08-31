# DQ Catalog webapp

A local, zero-install browser/filter/download/upload tool for this catalog.
Python **stdlib only** — no `pip install` needed.

## Run

```bash
python webapp/app.py          # defaults to port 8787
python webapp/app.py 9000     # or pick a port
```

Open the printed URL (`http://127.0.0.1:8787`). The server binds to
`127.0.0.1` only — it can push branches and open PRs on this repo's GitHub
remote, so it must stay local, never exposed on the network.

## What it does

- **Catalog** — browse every rule, filter by Object / Table / Field / Industry /
  Domain (chips combine as AND-across-facets, OR-within-a-facet) plus free-text
  search. Click a rule for the full parsed detail (description, DQ checks,
  fields, OptSel SQL).
- **Download** — from a rule's detail panel, enter a Source System ID and
  download an adapted copy with every `{SOURCE_SYSTEM}` / `{SOURCE_SYSTEM_ID}`
  token in the markdown replaced with that value.
- **Bulk download** — check individual rule cards (or **Select all filtered**
  to grab every rule matching the current Object/Table/Field/Industry/Domain
  filters at once), then **Download N rules**. Enter one Source System ID and
  get back a single `.zip` with each rule as its own adapted `.md` file inside.
- **Summary** — total rules / objects / tables, plus click-through
  distributions (rules per object, table, domain, criticality) that jump back
  into a pre-filtered Catalog view.
- **Upload** — drop one or more rule `.md` files. The backend auto-parses each
  one's Rule Header + Output Fields tables to pre-fill `domain`, `dataType`,
  `criticality`, `tables`, and `fields`; you review/edit (`object` and
  `industries` aren't reliably in the `.md`, so those start blank) and then
  **Push to Catalog**, which writes the files, updates `metadata.json`, and
  opens a PR (`catalog-app/add-...` branch) via `gh pr create` — it does not
  push straight to `main`.

## How it's built

- `app.py` — `http.server.ThreadingHTTPServer` + a small routing table. Git/PR
  operations run under a lock (`subprocess` calls to `git`/`gh`) so two
  concurrent uploads can't race on the same branch checkout.
- `rule_parser.py` — turns a rule `.md` into a structured dict: splits the
  document into heading sections, parses GFM pipe-tables generically, and
  pulls every `TABLE.FIELD` reference out of the Output Fields tables via
  regex (also catches multi-table calculated-field formulas).
- `static/` — plain HTML/CSS/JS, no build step, no framework. Visual system is
  vendored from `syniti-brand-kit` (`static/vendor/` — see `SOURCE.md` there)
  plus this app's own `app.css` component styles on the same tokens. Icons are
  pre-processed into `static/icons.js` (see `static/vendor/SOURCE.md`).

## Requirements

- Python 3.10+ (stdlib only, nothing to install).
- `git` and `gh` (GitHub CLI) on `PATH`, `gh` authenticated for this repo's
  remote — needed only for the Upload → Push flow, not for Catalog/Summary/
  Download.
