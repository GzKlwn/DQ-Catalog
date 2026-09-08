import os
import re
import json

# Load corrected metadata
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

rule_map = {r['name']: r for r in metadata['rules']}

def fix_rule_sections(rule_path, folder_name):
    """Fix Description, Fetch, Check, Return sections in markdown"""

    if folder_name not in rule_map:
        return False

    rule_meta = rule_map[folder_name]

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False

    # Get title from markdown
    title_match = re.search(r'^# DQ Rule: ACE_(\d+) - (.+?)$', content, re.MULTILINE)
    if not title_match:
        return False

    exact_title = title_match.group(2)
    primary_table = rule_meta['tables'][0] if rule_meta['tables'] else 'UNKNOWN'

    # Create proper sections
    new_description = f"""## Description

### 1. Functional/Business Description
This rule validates data integrity by ensuring: {exact_title.lower()}. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

### 2. Specific Relevancy Criteria/Scope
- **Primary Table:** {primary_table}
- **Related Tables:** {', '.join(rule_meta['tables'][1:]) if len(rule_meta['tables']) > 1 else 'N/A'}
- **Domain:** {rule_meta['domain']}
- **Scope:** All active records in {primary_table}
- **System Filter:** System_001 (as configured in Studio)

### 3. DQ Checks (Conditions)

- **Fetch** <br />
  Retrieves all candidate records from {primary_table} that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br />
  For each record in {primary_table}, evaluates the defined error conditions: {exact_title.lower()}. Flags records that violate the rule requirements.

- **Return** <br />
  Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.

"""

    # Replace description section
    old_desc_pattern = r'## Description\s*\n\n(.*?)(?=\n## Output Fields|\n## Logic)'
    content = re.sub(old_desc_pattern, new_description, content, flags=re.DOTALL)

    # Also update Data Domain in header
    content = re.sub(
        r'\| Data Domain \| [^|]+ \|',
        f'| Data Domain | {rule_meta["domain"]} |',
        content
    )

    try:
        with open(rule_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

# Process all ACE rules
rules_dir = 'rules'
fixed = 0

for folder in sorted(os.listdir(rules_dir)):
    if folder.startswith('ACE_DQ_'):
        rule_path = os.path.join(rules_dir, folder, f'{folder}.md')
        if os.path.isfile(rule_path):
            if fix_rule_sections(rule_path, folder):
                fixed += 1

print(f"Fixed Description/Fetch/Check/Return sections for {fixed} rules")
print(f"Also updated Data Domain fields to match corrected metadata")
