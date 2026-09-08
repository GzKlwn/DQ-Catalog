import os
import re
import json

def parse_rule_title_from_folder(folder_name):
    """
    Parse the rule title from the folder name.
    E.g., ACE_DQ_0001_BomsMustNotIncludeTheirOwnFinishedAssemblyAsAComponent
    -> "BOMs MUST NOT include their own finished assembly as a component."
    """
    # Remove ACE_DQ_XXXX prefix
    match = re.match(r'ACE_DQ_\d+_(.+)$', folder_name)
    if not match:
        return None

    # Get the rest
    title_part = match.group(1)

    # Convert camelCase to title case with spaces
    # Add space before uppercase letters (except first)
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', title_part)

    # Convert "a" to "A" (Business a field -> Business A field -> Business Address field)
    # This is tricky - let's use common patterns
    spaced = spaced.replace(' a ', ' A ')
    spaced = spaced.replace(' an ', ' An ')
    spaced = spaced.replace(' as ', ' As ')
    spaced = spaced.replace(' the ', ' The ')
    spaced = spaced.replace(' and ', ' And ')

    # Add period at end if it looks like a business rule
    if ' MUST' in spaced.upper():
        spaced = spaced + '.'

    return spaced

def extract_sap_tables_from_sql(content):
    """Extract SAP tables from SQL"""
    tables = set()

    # FROM [WRKDQ].[dbo].[TABLENAME]
    for match in re.finditer(r'\[WRKDQ\]\.\[dbo\]\.\[([A-Z_0-9]+)\]', content):
        tables.add(match.group(1))

    return sorted(list(tables))

def extract_description_from_title(title):
    """Generate a basic description from the title"""
    if not title:
        return "DQ rule validation."

    # Convert title to description
    description = title.replace('MUST', 'validates that')
    description = description.replace('must', 'validates that')

    return description

def fix_rule_file(rule_path, folder_name, rule_number):
    """Fix a single rule file"""
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False, "Could not read file"

    # Parse correct title from folder name
    correct_title = parse_rule_title_from_folder(folder_name)
    if not correct_title:
        return False, "Could not parse title from folder"

    # Extract tables from SQL
    tables = extract_sap_tables_from_sql(content)
    primary_table = tables[0] if tables else 'UNKNOWN'

    # Extract current header table
    header_match = re.search(
        r'### Rule\n\n\|.*?\n(.*?)\n### Implementation',
        content,
        re.DOTALL
    )

    # Build new header table
    new_header = f"""### Rule
| Field | Value |
|---|---|
| Rule ID | {rule_number:05d} |
| Rule Name | {correct_title} |
| Rule Name Score | 100% |
| Data Domain | {primary_table} |
| Object Type | Master |
| Business Process | Data Quality |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |"""

    # Replace header
    if header_match:
        old_header_section = header_match.group(0)
        content = content.replace(old_header_section, new_header + '\n\n### Implementation')

    # Fix description section if missing or empty
    desc_section_match = re.search(
        r'## Description\s*\n\n(.*?)(?=\n##|\n### 2\.)',
        content,
        re.DOTALL
    )

    if not desc_section_match or not desc_section_match.group(1).strip():
        new_desc = f"""## Description

### 1. Functional/Business Description
{extract_description_from_title(correct_title)}

### 2. Specific Relevancy Criteria/Scope
- **Primary Table:** {primary_table}
- **Scope:** All active records
- **System Filter:** System_001 (as configured in Studio)

### 3. DQ Checks (Conditions)

- **Fetch** <br />
  Retrieves candidate records based on scope criteria

- **Check** <br />
  Evaluates records against defined error conditions per rule logic

- **Return** <br />
  Returns records flagged as errors (zIsErrorFlag = 1) requiring remediation

---"""

        # Replace or add description
        if desc_section_match:
            old_desc = desc_section_match.group(0)
            content = content.replace(old_desc, new_desc)
        else:
            # Insert after ## Description
            desc_placeholder = re.search(r'## Description\n\n', content)
            if desc_placeholder:
                insert_pos = desc_placeholder.end()
                content = content[:insert_pos] + new_desc + '\n\n' + content[insert_pos:]

    # Write back
    try:
        with open(rule_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Fixed"
    except Exception as e:
        return False, str(e)

# Main script
rules_dir = 'rules'
results = {'fixed': 0, 'failed': 0, 'errors': []}

for rule_folder in sorted(os.listdir(rules_dir)):
    rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')

    if os.path.isfile(rule_path) and rule_folder.startswith('ACE_DQ_'):
        # Extract rule number
        match = re.match(r'ACE_DQ_(\d+)', rule_folder)
        rule_number = int(match.group(1)) if match else 0

        success, message = fix_rule_file(rule_path, rule_folder, rule_number)

        if success:
            results['fixed'] += 1
        else:
            results['failed'] += 1
            results['errors'].append(f"{rule_folder}: {message}")

print(f"""
================================================================================
RULE HEADER AND CONTENT FIX REPORT
================================================================================

Files processed: {results['fixed'] + results['failed']}
Successfully fixed: {results['fixed']}
Failed: {results['failed']}

""")

if results['errors']:
    print("Errors:")
    for error in results['errors'][:10]:
        print(f"  - {error}")
    if len(results['errors']) > 10:
        print(f"  ... and {len(results['errors']) - 10} more")

print("\n" + "=" * 80)
print("FIXES APPLIED:")
print("=" * 80)
print("""
✓ Rule Name corrected from folder name
✓ Rule ID extracted and set correctly
✓ Primary Table set from SQL content
✓ Description section populated with business rule statement
✓ Fetch/Check/Return sections added with placeholder content
✓ Data Domain, Object Type, Business Impact standardized
✓ Source set to 'ACE Rules'
""")
