import os
import json
import re
from pathlib import Path

def extract_metadata_from_rule_v2(rule_path):
    """
    Extract metadata from a single rule markdown file.
    - Tables: Extract from SQL CTEs (FROM and JOIN clauses)
    - Fields: Extract from zIsErrorFlag logic condition
    - Domain: Parse from Business Description and table context
    """
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    metadata = {}

    # Extract rule name from filename
    rule_dir = os.path.dirname(rule_path)
    rule_id = os.path.basename(rule_dir)
    metadata['name'] = rule_id

    # 1. EXTRACT TABLES from SQL CTEs
    tables_set = set()

    # Look for FROM clauses in SQL
    from_pattern = r'FROM\s+\[?(?:WRKDQ\.)?\[?dbo\]?\]?\.\[?([A-Z_0-9]+)\]?'
    for match in re.finditer(from_pattern, content, re.IGNORECASE):
        table = match.group(1).strip('[]')
        if table and len(table) <= 10 and table not in ['AS', 'WHERE', 'SELECT', 'AND', 'OR']:
            tables_set.add(table)

    # Look for JOIN clauses
    join_pattern = r'(?:INNER\s+JOIN|LEFT\s+JOIN|JOIN|FULL\s+JOIN)\s+\[?(?:WRKDQ\.)?\[?dbo\]?\]?\.\[?([A-Z_0-9]+)\]?'
    for match in re.finditer(join_pattern, content, re.IGNORECASE):
        table = match.group(1).strip('[]')
        if table and len(table) <= 10:
            tables_set.add(table)

    metadata['tables'] = sorted(list(tables_set)) if tables_set else []

    # 2. EXTRACT FIELDS from zIsErrorFlag logic
    fields_set = set()

    # Find the zIsErrorFlag CASE expression
    error_flag_pattern = r'CASE\s+.*?WHEN\s+(.*?)\s+THEN\s+[10]'
    match = re.search(error_flag_pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        case_logic = match.group(1)
        # Extract all field references: addr.[FIELDNAME] or [FIELDNAME]
        field_refs = re.findall(r'(?:addr\.|addressed\.|[a-z_]+\.)\[?([A-Z_0-9]+)\]?', case_logic)
        for field in field_refs:
            if field and field not in ['CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AND', 'OR']:
                fields_set.add(field)

    # If no CASE found, extract from Output Fields table
    if not fields_set:
        output_pattern = r'^\|\s*\d+\s*\|\s*[^\|]+\s*\|\s*([A-Z_0-9]+\.[A-Z_0-9]+)'
        for match in re.finditer(output_pattern, content, re.MULTILINE):
            table_field = match.group(1)
            field = table_field.split('.')[-1]
            if field and field not in ['Field', 'Value']:
                fields_set.add(field)

    metadata['fields'] = sorted(list(fields_set)) if fields_set else []

    # 3. EXTRACT DOMAIN from "Data Domain" field or Business Description
    domain_map = {
        'ADRC': 'Business Partner Master',
        'BUT020': 'Business Partner Master',
        'KNA1': 'Customer Master',
        'KNVV': 'Customer Master',
        'LFA1': 'Vendor Master',
        'LFBK': 'Vendor Master',
        'EQUI': 'Equipment Master',
        'MARA': 'Material Master',
        'MATS': 'Material Master',
        'AFPO': 'Internal Orders',
        'AUFM': 'Internal Orders',
        'VBAK': 'Sales Orders',
        'VBAP': 'Sales Orders',
        'EKKO': 'Purchase Orders',
        'EKPO': 'Purchase Orders',
        'BKPF': 'Accounting',
        'BSEG': 'Accounting',
        'MKPF': 'Physical Inventory',
        'MSEG': 'Material Movement',
        'RESB': 'Reservations',
        'AFIH': 'Equipment Master',
        'ROUT': 'Routing',
        'PLPO': 'Bill of Materials',
        'MKAL': 'Costing',
        'EKBE': 'Purchase Order History',
        'VBFA': 'Document Flow',
        'VBRK': 'Billing',
        'LIPS': 'Delivery Items',
        'LIKP': 'Delivery Headers',
        'KONV': 'Condition Records',
        'A017': 'Inspection Plans',
        'QAMR': 'Inspection Lots',
    }

    # Try to extract from Data Domain field
    domain_match = re.search(r'\|\s*Data Domain\s*\|\s*([^|]+)\s*\|', content)
    if domain_match:
        domain_raw = domain_match.group(1).strip()
        # If multiple domains, take the most specific one
        if ',' in domain_raw:
            domains = [d.strip() for d in domain_raw.split(',')]
            # Prefer more specific over generic
            metadata['domain'] = domains[0]
        else:
            metadata['domain'] = domain_raw
    elif metadata['tables']:
        # Map first table to domain
        first_table = metadata['tables'][0]
        metadata['domain'] = domain_map.get(first_table, 'Master Data')
    else:
        metadata['domain'] = 'Master Data'

    # Extract Object Type
    object_match = re.search(r'\|\s*Object Type\s*\|\s*([^|]+)\s*\|', content)
    if object_match:
        object_type = object_match.group(1).strip()
        metadata['object'] = object_type if object_type else "Unknown"
    else:
        metadata['object'] = 'Master'

    # Extract Business Impact -> Criticality
    impact_match = re.search(r'\|\s*Business Impact\s*\|\s*([^|]+)\s*\|', content)
    if impact_match:
        impact = impact_match.group(1).strip()
        criticality_map = {'High': 'High', 'Medium': 'Medium', 'Low': 'Low'}
        metadata['criticality'] = criticality_map.get(impact, 'Medium')
    else:
        metadata['criticality'] = 'Medium'

    # Extract description
    desc_match = re.search(r'### 1\. Functional/Business Description\s*\n(.*?)(?=\n###|\n---)', content, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()
        sentences = description.split('.')
        metadata['description'] = (sentences[0] + '.').strip()
    else:
        metadata['description'] = f"DQ rule {rule_id}"

    # Extract Business Process for industries
    process_match = re.search(r'\|\s*Business Process\s*\|\s*([^|]+)\s*\|', content)
    industries = []
    if process_match:
        process = process_match.group(1).strip()
        if 'Sales' in process or 'Order' in process or 'Delivery' in process:
            industries.append('Manufacturing')
        if 'Procurement' in process or 'Purchase' in process or 'Vendor' in process:
            industries.append('Manufacturing')
        if 'Finance' in process or 'Accounting' in process or 'Payable' in process or 'Receivable' in process:
            industries.append('Finance')
        if 'Production' in process or 'Material' in process or 'Manufacturing' in process or 'BOM' in process or 'Routing' in process:
            industries.append('Manufacturing')
        if 'HR' in process or 'Payroll' in process or 'Personnel' in process:
            industries.append('Finance')
        if 'Quality' in process or 'Inspection' in process:
            industries.append('Manufacturing')
        if 'Maintenance' in process or 'Equipment' in process:
            industries.append('Manufacturing')
        if 'Costing' in process or 'Budget' in process or 'Cost' in process:
            industries.append('Finance')

    if not industries:
        industries = ['Manufacturing', 'Finance']

    metadata['industries'] = list(set(industries))

    # Determine dataType
    metadata['dataType'] = 'Master Data' if 'Master' in metadata.get('domain', '') else 'Transactional Data'

    # Add source
    metadata['source'] = 'ACE Rules'

    return metadata

# Main script
if __name__ == '__main__':
    rules_dir = 'rules'
    all_rules = []

    # Process all rule folders
    for rule_folder in sorted(os.listdir(rules_dir)):
        rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')
        if os.path.isfile(rule_path):
            metadata = extract_metadata_from_rule_v2(rule_path)
            if metadata:
                all_rules.append(metadata)

    # Save updated metadata
    output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
    with open('metadata.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Updated metadata.json with {len(all_rules)} rules (improved extraction)")
    print(f"\nFirst 5 rules:")
    for i, rule in enumerate(all_rules[:5], 1):
        print(f"\n{i}. {rule['name']}")
        print(f"   Domain: {rule.get('domain')}")
        print(f"   Object: {rule.get('object')}")
        print(f"   Tables: {', '.join(rule.get('tables', []))}")
        fields_display = ', '.join(rule.get('fields', [])[:5])
        if len(rule.get('fields', [])) > 5:
            fields_display += '...'
        print(f"   Fields: {fields_display}")
