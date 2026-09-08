import os
import re
import json

def extract_correct_metadata_from_sql(rule_path, folder_name):
    """
    Extract CORRECT metadata by:
    1. Using the title from MD (which is correct)
    2. Extracting tables ONLY from SQL (not from description)
    3. Extracting fields from zIsErrorFlag logic in SQL
    """
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    metadata = {}

    # Get rule number and title from markdown (AUTHORITATIVE SOURCE)
    match = re.match(r'ACE_DQ_(\d+)_(.+)$', folder_name)
    if not match:
        return None

    rule_num = int(match.group(1))
    title_from_folder = re.sub(r'(?<!^)(?=[A-Z])', ' ', match.group(2))

    # But get the EXACT title from markdown title line
    title_match = re.search(r'^# DQ Rule: ACE_(\d+) - (.+?)$', content, re.MULTILINE)
    if title_match:
        exact_title = title_match.group(2)
    else:
        exact_title = title_from_folder

    metadata['name'] = folder_name

    # Extract tables ONLY from SQL section (not from description)
    tables_set = set()

    # Find SQL block
    sql_block = re.search(r'## SQL -- OptSel\s*\n```sql(.*?)```', content, re.DOTALL)
    if sql_block:
        sql_content = sql_block.group(1)

        # Extract from FROM and JOIN in SQL
        for match in re.finditer(r'\[WRKDQ\]\.\[dbo\]\.\[([A-Z_0-9]+)\]', sql_content):
            table = match.group(1)
            if table not in ['WRKDQ', 'dbo']:
                tables_set.add(table)

    metadata['tables'] = sorted(list(tables_set)) if tables_set else []

    # Extract fields ONLY from zIsErrorFlag CASE expression
    fields_set = set()

    # Find the CASE expression in SQL
    case_match = re.search(r'CASE\s+(.*?)END\s+AS\s+\[zIsErrorFlag\]', content, re.DOTALL | re.IGNORECASE)
    if case_match:
        case_logic = case_match.group(1)

        # Extract field references [FIELDNAME]
        for field_match in re.finditer(r'\[([A-Z_0-9]+)\]', case_logic):
            field = field_match.group(1)
            # Filter out SQL keywords and table names
            if field not in ['CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'SELECT', 'AND', 'OR'] and len(field) > 2:
                fields_set.add(field)

    metadata['fields'] = sorted(list(fields_set)) if fields_set else []

    # Map tables to correct domain
    domain_map = {
        'MAST': 'Bill of Materials',
        'STKO': 'Bill of Materials',
        'STPO': 'Bill of Materials',
        'ADRC': 'Business Partner Master',
        'BUT020': 'Business Partner Master',
        'EQUI': 'Equipment Master',
        'MARA': 'Material Master',
        'VBAK': 'Sales Orders',
        'EKKO': 'Purchase Orders',
        'AUFM': 'Internal Orders',
        'KONV': 'Pricing Records',
        'CRCA': 'Costing',
        'QAMR': 'Inspection Lots',
    }

    if metadata['tables']:
        primary_table = metadata['tables'][0]
        metadata['domain'] = domain_map.get(primary_table, 'Master Data')
    else:
        metadata['domain'] = 'Master Data'

    # Object Type from header (if reasonable)
    object_match = re.search(r'\| Object Type \| ([^|]+) \|', content)
    metadata['object'] = object_match.group(1).strip() if object_match else 'Master'

    # Criticality
    impact_match = re.search(r'\| Business Impact \| ([^|]+) \|', content)
    if impact_match:
        impact = impact_match.group(1).strip()
        metadata['criticality'] = {'High': 'High', 'Medium': 'Medium', 'Low': 'Low'}.get(impact, 'High')
    else:
        metadata['criticality'] = 'High'

    # Description - extract from description section
    desc_match = re.search(r'### 1\. Functional/Business Description\s*\n(.+?)(?=\n###|\n---)', content, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        sentences = [s.strip() for s in desc.split('.') if s.strip()]
        if sentences:
            metadata['description'] = sentences[0] + '.'
        else:
            metadata['description'] = exact_title
    else:
        metadata['description'] = exact_title

    # Industries based on domain and business process
    industries = set()

    if any(kw in metadata['domain'] for kw in ['Bill', 'Material', 'Equipment', 'Sales', 'Order', 'Production', 'Inventory', 'Inspection']):
        industries.add('Manufacturing')

    if any(kw in metadata['domain'] for kw in ['Billing', 'Accounting', 'Costing', 'Pricing']):
        industries.add('Finance')

    if not industries:
        industries = {'Manufacturing', 'Finance'}

    metadata['industries'] = sorted(list(industries))

    # DataType
    metadata['dataType'] = 'Master Data' if 'Master' in metadata['domain'] or 'BOM' in metadata['domain'] else 'Transactional Data'

    # Source
    metadata['source'] = 'ACE Rules'

    return metadata

# Process all rules
rules_dir = 'rules'
all_rules = []

for rule_folder in sorted(os.listdir(rules_dir)):
    rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')
    if os.path.isfile(rule_path) and rule_folder.startswith('ACE_DQ_'):
        metadata = extract_correct_metadata_from_sql(rule_path, rule_folder)
        if metadata:
            all_rules.append(metadata)

# Save
output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Regenerated metadata.json with {len(all_rules)} rules")
print("Using SQL sections as authoritative source for tables and fields")
print("\nSample corrected rule:")
for rule in all_rules[:1]:
    print(f"\n{rule['name']}")
    print(f"  Domain: {rule['domain']}")
    print(f"  Tables: {', '.join(rule['tables'])}")
    print(f"  Fields: {len(rule['fields'])} fields")
    print(f"  Description: {rule['description'][:80]}")
