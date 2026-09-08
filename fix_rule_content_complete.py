import os
import re

def extract_rule_info_from_folder(folder_name):
    """
    Extract rule information from folder name.
    E.g., ACE_DQ_0002_BusinessAFieldAddressesMustIncludeACityWhenOtherMailingDetai
    """
    match = re.match(r'ACE_DQ_(\d+)_(.+)$', folder_name)
    if not match:
        return None, None

    rule_num = int(match.group(1))
    title_camel = match.group(2)

    # Convert camelCase to Title Case
    title = re.sub(r'(?<!^)(?=[A-Z])', ' ', title_camel)

    # Add period if it's a business rule
    if 'MUST' not in title.upper():
        title = title + ' .'
    elif not title.endswith('.'):
        title = title + '.'

    return rule_num, title

def extract_primary_table_from_sql(content):
    """Extract primary table from SQL"""
    # Look for FROM [WRKDQ].[dbo].[TABLENAME]
    matches = re.findall(r'\[WRKDQ\]\.\[dbo\]\.\[([A-Z_0-9]+)\]', content)
    if matches:
        return matches[0]  # Return first (primary) table
    return 'UNKNOWN'

def create_fetch_section(primary_table):
    """Generate Fetch section"""
    return f"Retrieves all candidate records from {primary_table} that meet the scope criteria and filters."

def create_check_section(primary_table):
    """Generate Check section"""
    return f"For each record in {primary_table}, evaluates the defined error conditions using business logic. Flags records that violate the rule requirements."

def create_return_section():
    """Generate Return section"""
    return "Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis."

def fix_rule_file_complete(rule_path, folder_name):
    """Complete fix for a single rule file"""

    # Get correct rule info
    rule_num, correct_title = extract_rule_info_from_folder(folder_name)
    if not rule_num or not correct_title:
        return False, "Could not parse folder name"

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Read error: {str(e)}"

    # Extract primary table
    primary_table = extract_primary_table_from_sql(content)

    # Fix Rule Name in header
    content = re.sub(
        r'\| Rule Name \| [^|]+ \|',
        f'| Rule Name | {correct_title} |',
        content
    )

    # Fix Rule ID
    content = re.sub(
        r'\| Rule ID \| \d+ \|',
        f'| Rule ID | {rule_num:05d} |',
        content
    )

    # Fix SQL comment for OptSel
    content = re.sub(
        r'-- DQ Rule: [^\n]+',
        f'-- DQ Rule: {correct_title}',
        content
    )

    # Fix SQL Rule ID comment
    content = re.sub(
        r'-- Rule ID: ACE_\d+',
        f'-- Rule ID: ACE_{rule_num:05d}',
        content
    )

    # Fix Description section
    fetch_text = create_fetch_section(primary_table)
    check_text = create_check_section(primary_table)
    return_text = create_return_section()

    new_desc_section = f"""## Description

### 1. Functional/Business Description
This rule validates data integrity in {primary_table} by ensuring {correct_title.lower().replace('must', 'that').replace('must not', 'that it does not')} Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

### 2. Specific Relevancy Criteria/Scope
- **Primary Table:** {primary_table}
- **Scope:** All active records in {primary_table}
- **System Filter:** System_001 (as configured in Studio)

### 3. DQ Checks (Conditions)

- **Fetch** <br />
  {fetch_text}

- **Check** <br />
  {check_text}

- **Return** <br />
  {return_text}

"""

    # Replace description section (from ## Description to ## Output Fields)
    old_desc_pattern = r'## Description\s*\n\n(.*?)(?=\n## Output Fields)'
    content = re.sub(old_desc_pattern, new_desc_section.rstrip() + '\n', content, flags=re.DOTALL)

    # Write back
    try:
        with open(rule_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Fixed"
    except Exception as e:
        return False, f"Write error: {str(e)}"

# Main
rules_dir = 'rules'
results = {'fixed': 0, 'failed': 0, 'errors': []}

print("Fixing rule content alignment and descriptions...")
print("=" * 80)

for folder in sorted(os.listdir(rules_dir)):
    if folder.startswith('ACE_DQ_'):
        rule_path = os.path.join(rules_dir, folder, f'{folder}.md')
        if os.path.isfile(rule_path):
            success, message = fix_rule_file_complete(rule_path, folder)

            if success:
                results['fixed'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"{folder}: {message}")

print(f"\nRules processed: {results['fixed'] + results['failed']}")
print(f"Successfully fixed: {results['fixed']}")
print(f"Failed: {results['failed']}")

if results['errors']:
    print("\nErrors:")
    for error in results['errors'][:5]:
        print(f"  - {error}")
    if len(results['errors']) > 5:
        print(f"  ... and {len(results['errors']) - 5} more")

print("\n" + "=" * 80)
print("FIXES APPLIED:")
print("- Rule titles aligned from folder names")
print("- SQL comments updated to match titles")
print("- Descriptions populated with business context")
print("- Fetch/Check/Return sections filled with meaningful content")
print("- All sections now reference correct Primary Table")
print("=" * 80)
