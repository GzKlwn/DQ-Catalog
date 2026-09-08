import os
import re
import json

def extract_fetch_check_return_from_markdown(rule_path):
    """Extract Fetch, Check, Return with better boundary detection"""

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None, None, None

    # Find the Description section
    desc_section_match = re.search(r'## Description\s*\n\n(.*?)(?=\n## Output Fields|\n## Logic)', content, re.DOTALL)
    if not desc_section_match:
        return "", "", ""

    desc_body = desc_section_match.group(1)

    results = {}

    for label in ("Fetch", "Check", "Return"):
        # Pattern: - **Label** <br /> content until next dash-bold or double newline
        m = re.search(
            rf'-\s*\*\*{label}\*\*\s*<br\s*/?>\s*(.*?)(?=\n\n-\s*\*\*|$)',
            desc_body,
            re.DOTALL
        )
        if m:
            # Clean up: remove extra whitespace but preserve single spaces
            cleaned = ' '.join(m.group(1).split())
            results[label.lower()] = cleaned
        else:
            results[label.lower()] = ""

    return results.get('fetch', ''), results.get('check', ''), results.get('return', '')

# Load current metadata
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

# Extract from markdown and update metadata
rules_dir = 'rules'
updated = 0

for rule in metadata['rules']:
    rule_name = rule['name']
    rule_path = os.path.join(rules_dir, rule_name, f'{rule_name}.md')

    if os.path.isfile(rule_path):
        fetch, check, ret = extract_fetch_check_return_from_markdown(rule_path)

        if fetch or check or ret:
            rule['fetch'] = fetch
            rule['check'] = check
            rule['return'] = ret
            updated += 1

# Save updated metadata
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"Fixed extraction for {updated} rules in metadata.json")

# Verify
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

sample = next((r for r in metadata['rules'] if r['name'].startswith('ACE_DQ_0008')), None)
if sample:
    print(f"\nVerification (ACE_0008):")
    print(f"\n  Description ({len(sample.get('description', ''))} chars):")
    print(f"    {sample.get('description', '')[:80]}")
    print(f"\n  Fetch ({len(sample.get('fetch', ''))} chars):")
    print(f"    {sample.get('fetch', '')[:80]}")
    print(f"\n  Check ({len(sample.get('check', ''))} chars):")
    print(f"    {sample.get('check', '')[:80]}")
    print(f"\n  Return ({len(sample.get('return', ''))} chars):")
    print(f"    {sample.get('return', '')[:80]}")
