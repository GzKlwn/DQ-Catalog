import os
import re
import json

def extract_fetch_check_return_from_markdown(rule_path):
    """Extract Fetch, Check, Return from markdown file"""

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None, None, None

    # Extract Fetch
    fetch_match = re.search(r'-\s*\*\*Fetch\*\*\s*<br\s*/?>\s*(.*?)(?=\n\n-\s*\*\*|\Z)', content, re.DOTALL)
    fetch = ' '.join(fetch_match.group(1).split()) if fetch_match else ""

    # Extract Check
    check_match = re.search(r'-\s*\*\*Check\*\*\s*<br\s*/?>\s*(.*?)(?=\n\n-\s*\*\*|\Z)', content, re.DOTALL)
    check = ' '.join(check_match.group(1).split()) if check_match else ""

    # Extract Return
    return_match = re.search(r'-\s*\*\*Return\*\*\s*<br\s*/?>\s*(.*?)(?=\n\n-\s*\*\*|\Z)', content, re.DOTALL)
    ret = ' '.join(return_match.group(1).split()) if return_match else ""

    return fetch, check, ret

# Load current metadata
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

# Extract from markdown and add to metadata
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

print(f"Added fetch/check/return fields to {updated} rules in metadata.json")

# Verify
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

sample = next((r for r in metadata['rules'] if r['name'].startswith('ACE_DQ_0008')), None)
if sample:
    print(f"\nSample (ACE_0008):")
    print(f"  Fetch: {sample.get('fetch', '')[:70] if sample.get('fetch') else '(empty)'}")
    print(f"  Check: {sample.get('check', '')[:70] if sample.get('check') else '(empty)'}")
    print(f"  Return: {sample.get('return', '')[:70] if sample.get('return') else '(empty)'}")
