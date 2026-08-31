# DQ Catalog

Central catalog of DQ rules for the Syniti Methodology Studio and related applications.

## Structure

```
dq-catalog/
├── rules/
│   ├── rule-name-1/
│   │   └── rule-name-1.md       (Rule definition: spec, OptSel, RptSel, metadata)
│   ├── rule-name-2/
│   │   └── rule-name-2.md
│   └── ...
└── metadata.json                 (Central registry of all rules)
```

## Adding a Rule

1. Create a folder: `rules/{rule-name}/`
2. Add the rule markdown: `rules/{rule-name}/{rule-name}.md`
3. Update `metadata.json` with the rule metadata:
   - `name`: Rule identifier (matches folder and markdown filename)
   - `object`: SAP object (e.g., "Customer", "Order", "Product")
   - `dataType`: "Master Data" or "Transactional Data"
   - `description`: Brief business description of the rule
   - `tables`: List of affected SAP tables (e.g., ["KNA1", "KNVV"])
   - `criticality`: High, Medium, or Low
   - `industries`: Array of applicable industries (e.g., ["Manufacturing", "Finance"])
   - `domain`: Data Domain from the rule's `## Rule Header` table (e.g., "Customer Master")
   - `fields`: List of individual `TABLE.FIELD` codes referenced across the rule's Output Fields tables (e.g., ["KUNNR", "ZTERM"])

Or skip steps 1–3 and use the **webapp** (below) — it parses `domain`, `dataType`,
`criticality`, `tables`, and `fields` straight out of an uploaded `.md` for you.

## Metadata Schema

Each rule entry in `metadata.json` must have:

```json
{
  "name": "rule-name",
  "object": "Object Name",
  "dataType": "Master Data|Transactional Data",
  "description": "Brief business description of what the rule validates",
  "tables": ["TABLE1", "TABLE2"],
  "criticality": "High|Medium|Low",
  "industries": ["Industry1", "Industry2"],
  "domain": "Data Domain, e.g. Customer Master",
  "fields": ["FIELD1", "FIELD2"]
}
```

## Webapp

`webapp/` is a local, zero-install browser/filter/download/upload tool for this
catalog — see [`webapp/README.md`](webapp/README.md). Run `python webapp/app.py`
and open `http://127.0.0.1:8787` to:

- Browse and filter rules by object, table, field, industry, and domain
- Download a rule with `{SOURCE_SYSTEM}` / `{SOURCE_SYSTEM_ID}` substituted for a
  source system ID you provide
- See a summary dashboard of rule counts/distributions, click-through into the
  filtered catalog view
- Upload one or more rule `.md` files, review the auto-parsed metadata, and push
  them to this catalog as a PR

## Usage

### Studio Integration
- Studio pulls this catalog periodically
- When a user enters a rule name, Studio checks if it matches a catalog rule
- If matched: auto-populate from the markdown
- If not matched: derive and enhance as normal

## Git Workflow

```bash
git pull origin main  # Keep catalog up to date
git add rules/ metadata.json
git commit -m "feat: Add new rule {name}"
git push origin main
```
