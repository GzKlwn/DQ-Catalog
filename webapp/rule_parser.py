"""Parse a DQ-Catalog rule markdown file into a structured dict.

Stdlib-only (re + dataclasses). See dq-catalog/README.md for the markdown
shape this expects (Rule Header table, Implementation table, Description,
Output Fields sub-tables, SQL -- OptSel / RptSel fenced blocks).
"""
from __future__ import annotations

import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
SEPARATOR_CELL_RE = re.compile(r":?-{3,}:?")
TABLE_FIELD_RE = re.compile(r"\b([A-Z][A-Z0-9_]{1,29})\.([A-Za-z][A-Za-z0-9_]{0,29})\b")

# {SOURCE_SYSTEM} appears in view names; {SOURCE_SYSTEM_ID} in filter values /
# the Implementation table. The webapp asks the user for one value and
# substitutes both tokens with it.
SUBSTITUTION_TOKENS = ("{SOURCE_SYSTEM_ID}", "{SOURCE_SYSTEM}")


def substitute_source_system(markdown_text: str, system_id: str) -> str:
    out = markdown_text
    for token in SUBSTITUTION_TOKENS:
        out = out.replace(token, system_id)
    return out


def parse_pipe_table(block_lines: list[str]) -> list[dict[str, str]]:
    """Parse a contiguous block of `| a | b |` lines into row dicts keyed by
    the header row. Skips the `|---|---|` separator line."""
    rows: list[list[str]] = []
    for line in block_lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and all(SEPARATOR_CELL_RE.fullmatch(c) or c == "" for c in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return []
    header, data = rows[0], rows[1:]
    return [dict(zip(header, r)) for r in data]


def extract_all_tables(text: str) -> list[list[dict[str, str]]]:
    """Find every contiguous pipe-table block in the document, parsed."""
    lines = text.splitlines()
    tables: list[list[dict[str, str]]] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            j = i
            block = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1
            parsed = parse_pipe_table(block)
            if parsed:
                tables.append(parsed)
            i = j
        else:
            i += 1
    return tables


def parse_sections(text: str) -> list[dict]:
    """Split the doc into {level, title, body} per heading. body = every
    line until the next heading of the same or shallower level."""
    lines = text.splitlines()
    headings = []
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))
    sections = []
    for idx, (i, level, title) in enumerate(headings):
        end = len(lines)
        for j in range(idx + 1, len(headings)):
            if headings[j][1] <= level:
                end = headings[j][0]
                break
        sections.append({"level": level, "title": title, "body": "\n".join(lines[i + 1 : end])})
    return sections


def find_section(sections: list[dict], title: str, level: int | None = None) -> dict | None:
    for s in sections:
        if s["title"].strip().lower() == title.strip().lower() and (level is None or s["level"] == level):
            return s
    return None


def _kv_table(body: str) -> dict[str, str]:
    tables = extract_all_tables(body)
    if not tables:
        return {}
    rows = tables[0]
    out = {}
    for row in rows:
        keys = list(row.keys())
        if len(keys) >= 2:
            out[row[keys[0]]] = row[keys[1]]
    return out


DATA_TYPE_MAP = {
    "master": "Master Data",
    "master data": "Master Data",
    "transactional": "Transactional Data",
    "transactional data": "Transactional Data",
}


def _normalize_data_type(object_type: str) -> str:
    key = (object_type or "").strip().lower()
    return DATA_TYPE_MAP.get(key, object_type.strip() if object_type else "")


def _extract_description_paragraph(description_body: str) -> str:
    m = re.search(
        r"\*\*1\.\s*Functional/Business Description\*\*\s*\n+(.*?)(?=\n\n\*\*2\.|\Z)",
        description_body,
        re.DOTALL,
    )
    if not m:
        return ""
    return " ".join(m.group(1).split())


def _extract_fetch_check_return(description_body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for label in ("Fetch", "Check", "Return"):
        m = re.search(
            rf"-\s*\*\*{label}\*\*\s*<br\s*/?>\s*(.*?)(?=\n\n-\s*\*\*|\n##|\Z)",
            description_body,
            re.DOTALL,
        )
        if m:
            cleaned = re.sub(r"<br\s*/?>", " ", m.group(1))
            out[label.lower()] = " ".join(cleaned.split())
    return out


def _extract_tables_and_fields(sections: list[dict]) -> tuple[list[str], list[str]]:
    """Scan every 'X Fields' sub-table for a 'Table.Field' column and pull
    every TABLE.FIELD reference out of it (handles both plain refs and
    calculated-field formulas that reference multiple tables)."""
    tables_seen: dict[str, None] = {}
    fields_seen: dict[str, None] = {}
    for s in sections:
        if not s["title"].lower().endswith("fields"):
            continue
        for table in extract_all_tables(s["body"]):
            if "Table.Field" not in (table[0].keys() if table else []):
                continue
            for row in table:
                cell = row.get("Table.Field", "")
                for tbl, fld in TABLE_FIELD_RE.findall(cell):
                    tables_seen[tbl] = None
                    fields_seen[fld] = None
    return list(tables_seen.keys()), list(fields_seen.keys())


def _extract_sql_block(sections: list[dict], title_prefix: str) -> str:
    for s in sections:
        if s["title"].strip().lower().startswith(title_prefix.lower()):
            m = re.search(r"```sql\n(.*?)```", s["body"], re.DOTALL)
            if m:
                return m.group(1).rstrip()
    return ""


def parse(markdown_text: str) -> dict:
    """Parse a rule .md into a structured dict used both for the detail
    panel and for the upload-review auto-fill."""
    sections = parse_sections(markdown_text)

    first_line = markdown_text.splitlines()[0] if markdown_text else ""
    title = re.sub(r"^#\s*(DQ Rule:\s*)?", "", first_line).strip()

    rule_kv = _kv_table((find_section(sections, "Rule", 3) or {}).get("body", ""))
    impl_kv = _kv_table((find_section(sections, "Implementation", 3) or {}).get("body", ""))
    desc_section = find_section(sections, "Description", 2) or {}
    desc_body = desc_section.get("body", "")

    tables, fields = _extract_tables_and_fields(sections)

    optsel_sql = _extract_sql_block(sections, "SQL -- OptSel") or _extract_sql_block(sections, "SQL")
    rptsel_sql = _extract_sql_block(sections, "SQL -- RptSel")

    return {
        "title": title,
        "skpRuleId": rule_kv.get("SKP Rule ID", ""),
        "ruleName": rule_kv.get("Rule Name", title),
        "domain": rule_kv.get("Data Domain", ""),
        "objectType": rule_kv.get("Object Type", ""),
        "dataType": _normalize_data_type(rule_kv.get("Object Type", "")),
        "criticality": rule_kv.get("Business Impact", ""),
        "ruleType": rule_kv.get("Rule Type", ""),
        "source": rule_kv.get("Source", ""),
        "dqopsId": impl_kv.get("DQOps ID", ""),
        "description": _extract_description_paragraph(desc_body),
        "checks": _extract_fetch_check_return(desc_body),
        "tables": tables,
        "fields": fields,
        "optselSql": optsel_sql,
        "rptselSql": rptsel_sql,
        "raw": markdown_text,
    }
