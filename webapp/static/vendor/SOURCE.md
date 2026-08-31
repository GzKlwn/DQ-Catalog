# Vendored brand assets

Copied verbatim from `syniti-brand-kit` (kit snapshot v1.0/v1.1, 2026-07-04/07)
so the DQ-Catalog webapp stays self-contained and portable — no dependency on
`syniti-brand-kit` existing at a sibling path on whatever machine runs this app.

| File | Origin |
|---|---|
| `tokens.css` | `syniti-brand-kit/tokens/tokens.css` |
| `patterns.css` | `syniti-brand-kit/patterns/patterns.css` |

Per the kit's own `CLAUDE.md`: **tokens are the source of truth.** If the brand
ramp, radii, or spacing change upstream, re-copy these two files rather than
hand-editing the values here.

## Icons (`../icons.js`)

`webapp/static/icons.js` (one level up from this file) holds the icon markup
used by the app: `Rule-Management, Search, Filter, Download, Upload,
Finance-Chart, Database-Table, Check, Close, Pie-Chart`, taken from
`syniti-brand-kit/icons/sets/white/*.svg` and processed per
`syniti-brand-kit/icons/ICONS.md` §3 — every `id`/`url(#...)`/`href="#..."`
namespaced per-icon, and the hardcoded `fill: #f7f7f7` converted to
`fill: currentColor` so each icon inherits `color` from its container.

To add another icon or refresh these from an updated brand kit, re-run:

```python
import re, json
icons = ["Rule-Management", "Search", ...]  # names from sets/white/*.svg
out = {}
for name in icons:
    svg = open(f"sets/white/{name}.svg", encoding="utf-8").read()
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    for old_id in set(re.findall(r'id="([^"]+)"', svg)):
        new_id = "ic-" + re.sub(r"[^a-zA-Z0-9]", "", name) + "-" + old_id
        svg = svg.replace(f'id="{old_id}"', f'id="{new_id}"')
        svg = svg.replace(f"url(#{old_id})", f"url(#{new_id})")
        svg = svg.replace(f'href="#{old_id}"', f'href="#{new_id}"')
    svg = re.sub(r"fill:\s*#[0-9a-fA-F]{3,6};?", "fill: currentColor;", svg)
    svg = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', 'fill="currentColor"', svg)
    out[name] = svg.strip()
# write: "export const ICONS = " + json.dumps(out, indent=2) + ";\n"
```
