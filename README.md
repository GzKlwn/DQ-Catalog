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
  "industries": ["Industry1", "Industry2"]
}
```

## Usage

### Studio Integration
- Studio pulls this catalog periodically
- When a user enters a rule name, Studio checks if it matches a catalog rule
- If matched: auto-populate from the markdown
- If not matched: derive and enhance as normal

### Webapp Integration
- Webapp clones this repo and reads rules as needed
- Can filter by metadata (object, dataType, criticality, industries, tables)

## Git Workflow

```bash
git pull origin main  # Keep catalog up to date
git add rules/ metadata.json
git commit -m "feat: Add new rule {name}"
git push origin main
```
