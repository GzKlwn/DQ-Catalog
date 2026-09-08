import os
import re
import json

# Load metadata
with open('metadata.json', 'r') as f:
    metadata = json.load(f)

rule_map = {r['name']: r for r in metadata['rules']}

def fix_inline_content(rule_path, folder_name):
    """Put Fetch/Check/Return content inline with <br /> tags"""

    if folder_name not in rule_map:
        return False

    rule_meta = rule_map[folder_name]

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False

    # Get title
    title_match = re.search(r'^# DQ Rule: ACE_(\d+) - (.+?)$', content, re.MULTILINE)
    if not title_match:
        return False

    exact_title = title_match.group(2)
    primary_table = rule_meta['tables'][0] if rule_meta['tables'] else 'UNKNOWN'

    # FORMAT WITH INLINE CONTENT (content on same line as <br />)
    new_description = f"""## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: {exact_title.lower()}. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** {primary_table}
- **Related Tables:** {', '.join(rule_meta['tables'][1:]) if len(rule_meta['tables']) > 1 else 'N/A'}
- **Domain:** {rule_meta['domain']}
- **Scope:** All active records in {primary_table}
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from {primary_table} that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in {primary_table}, evaluates the defined error conditions: {exact_title.lower()}. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.

"""

    # Replace description section
    old_desc_pattern = r'## Description\s*\n\n(.*?)(?=\n## Output Fields|\n## Logic)'

    if re.search(old_desc_pattern, content, re.DOTALL):
        content = re.sub(old_desc_pattern, new_description, content, flags=re.DOTALL)
    else:
        # Fallback - replace until Output Fields
        content = re.sub(
            r'## Description.*?(?=\n## Output Fields)',
            new_description.rstrip(),
            content,
            flags=re.DOTALL
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

print("Converting Fetch/Check/Return to inline format...")
print("(Putting content on same line as <br /> for better parser compatibility)\n")

for folder in sorted(os.listdir(rules_dir)):
    if folder.startswith('ACE_DQ_'):
        rule_path = os.path.join(rules_dir, folder, f'{folder}.md')
        if os.path.isfile(rule_path):
            if fix_inline_content(rule_path, folder):
                fixed += 1

print(f"Fixed inline content format for {fixed} rules")
print("\nFormat change:")
print('  FROM: - **Fetch** <br />')
print('        Retrieves all candidate records...')
print('')
print('  TO:   - **Fetch** <br /> Retrieves all candidate records...')
print("\nThis should help the webapp parser extract content correctly")
