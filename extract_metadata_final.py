import os
import json
import re

def extract_metadata_final(rule_path):
    """
    Final extraction with improved domain mapping based on SAP tables
    """
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    metadata = {}
    rule_dir = os.path.dirname(rule_path)
    rule_id = os.path.basename(rule_dir)
    metadata['name'] = rule_id

    # Comprehensive SAP Table to Domain mapping
    domain_map = {
        # Business Partner
        'KNA1': 'Customer Master', 'KNVV': 'Customer Master', 'KNB1': 'Customer Master',
        'LFA1': 'Vendor Master', 'LFB1': 'Vendor Master', 'LFBK': 'Vendor Master',
        'ADRC': 'Business Partner Master', 'BUT020': 'Business Partner Master', 'BUT000': 'Business Partner Master',
        # Material/Product
        'MARA': 'Material Master', 'MATS': 'Material Master', 'MARC': 'Material Master',
        'MAST': 'Bill of Materials', 'STKO': 'Bill of Materials', 'STPO': 'Bill of Materials',
        'PLPO': 'Bill of Materials',
        # Equipment
        'EQUI': 'Equipment Master', 'EQKT': 'Equipment Master', 'EQFP': 'Equipment Master', 'AFIH': 'Equipment Master',
        # Maintenance/Internal Orders
        'AUFM': 'Internal Orders', 'AFPO': 'Internal Orders', 'AFRU': 'Internal Orders',
        # Routing
        'ROUT': 'Routing', 'PLNT': 'Routing',
        # Inspection
        'A017': 'Inspection Plans', 'QAMR': 'Inspection Lots', 'QAPE': 'Inspection Lots',
        # Sales
        'VBAK': 'Sales Orders', 'VBAP': 'Sales Orders', 'VBAS': 'Sales Orders',
        'LIKP': 'Delivery Headers', 'LIPS': 'Delivery Items',
        'VBRK': 'Billing Documents', 'VBRP': 'Billing Documents',
        'KNVP': 'Customer Pricing', 'KONV': 'Pricing Records',
        # Procurement
        'EKKO': 'Purchase Orders', 'EKPO': 'Purchase Orders', 'EKBE': 'Purchase Order History',
        'RESB': 'Reservations',
        # Accounting
        'BKPF': 'Accounting Documents', 'BSEG': 'Accounting Documents',
        'COEP': 'Cost Accounting', 'MKAL': 'Costing',
        # Physical Inventory
        'MKPF': 'Physical Inventory', 'MSEG': 'Physical Inventory',
        # Storage
        'LAGP': 'Storage Bins', 'LQUA': 'Storage Bins',
        # Project
        'PROJ': 'Project Master', 'PRPS': 'Project Master', 'PRCT': 'Project Master', 'PRBU': 'Project Master',
    }

    # Extract tables from scope section
    tables_set = set()
    scope_pattern = r'### 2\. Specific Relevancy Criteria/Scope.*?(?=\n###|\n---)'
    scope_match = re.search(scope_pattern, content, re.DOTALL)

    if scope_match:
        scope_section = scope_match.group(0)
        # Look for table names
        table_patterns = [
            r'(?:Primary|Related)? ?Table[s]?:\s*([A-Z_0-9]+(?:\s*,\s*[A-Z_0-9]+)*)',
            r'- \*\*Table[s]?:\*\*\s*([A-Z_0-9]+(?:\s*,\s*[A-Z_0-9]+)*)',
            r'\*\*Table[s]?:\*\*\s*([A-Z_0-9]+(?:\s*,\s*[A-Z_0-9]+)*)',
        ]
        for pattern in table_patterns:
            for match in re.finditer(pattern, scope_section):
                tables_str = match.group(1).strip()
                for table in [t.strip() for t in tables_str.split(',')]:
                    if table and len(table) <= 10 and table.isupper():
                        tables_set.add(table)

    # Fallback: extract from SQL
    if not tables_set:
        for match in re.finditer(r'\[WRKDQ\]\.\[dbo\]\.\[([A-Z_0-9]+)\]', content, re.IGNORECASE):
            tables_set.add(match.group(1))

    metadata['tables'] = sorted(list(tables_set))

    # Extract fields from zIsErrorFlag logic
    fields_set = set()
    error_flag_pattern = r'WHEN\s+(.*?)\s+THEN\s+[10]'
    for match in re.finditer(error_flag_pattern, content, re.DOTALL | re.IGNORECASE):
        logic = match.group(1)
        for field_match in re.finditer(r'\[([A-Z_0-9]+)\]', logic):
            field = field_match.group(1)
            if field not in ['CASE', 'WHEN', 'THEN', 'ELSE', 'END']:
                fields_set.add(field)

    metadata['fields'] = sorted(list(fields_set))

    # Extract domain - prioritize from Data Domain field in header
    domain_match = re.search(r'\|\s*Data Domain\s*\|\s*([^|]+)\s*\|', content)
    if domain_match:
        domain_raw = domain_match.group(1).strip()
        # Clean up and take first domain
        domain = domain_raw.split(',')[0].strip()
        # Handle known incorrect mappings
        if domain == 'Address Master':
            metadata['domain'] = 'Business Partner Master'
        elif domain in domain_map.values():
            metadata['domain'] = domain
        else:
            # Try mapping from tables
            if metadata['tables']:
                metadata['domain'] = domain_map.get(metadata['tables'][0], domain)
            else:
                metadata['domain'] = domain
    else:
        # Map from tables
        if metadata['tables']:
            metadata['domain'] = domain_map.get(metadata['tables'][0], 'Master Data')
        else:
            metadata['domain'] = 'Master Data'

    # Object Type
    object_match = re.search(r'\|\s*Object Type\s*\|\s*([^|]+)\s*\|', content)
    metadata['object'] = object_match.group(1).strip() if object_match else 'Master'

    # Criticality
    impact_match = re.search(r'\|\s*Business Impact\s*\|\s*([^|]+)\s*\|', content)
    if impact_match:
        impact = impact_match.group(1).strip()
        metadata['criticality'] = {'High': 'High', 'Medium': 'Medium', 'Low': 'Low'}.get(impact, 'Medium')
    else:
        metadata['criticality'] = 'Medium'

    # Description
    desc_match = re.search(r'### 1\. Functional/Business Description\s*\n(.*?)(?=\n###|\n---|\n\*\*)', content, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        sentences = [s.strip() for s in desc.split('.') if s.strip()]
        if sentences:
            metadata['description'] = sentences[0] + '.'
        else:
            metadata['description'] = f"DQ rule {rule_id}"
    else:
        metadata['description'] = f"DQ rule {rule_id}"

    # Industries
    process_match = re.search(r'\|\s*Business Process\s*\|\s*([^|]+)\s*\|', content)
    industries = set()
    if process_match:
        process = process_match.group(1).strip()
        if any(x in process for x in ['Sales', 'Order', 'Delivery', 'Procurement', 'Purchase', 'Vendor', 'Production', 'BOM', 'Routing', 'Quality', 'Inspection', 'Maintenance', 'Equipment', 'Material']):
            industries.add('Manufacturing')
        if any(x in process for x in ['Finance', 'Accounting', 'Payable', 'Receivable', 'Billing', 'Costing', 'Cost']):
            industries.add('Finance')

    metadata['industries'] = sorted(list(industries)) if industries else ['Manufacturing', 'Finance']

    # DataType
    if 'Master' in metadata['domain'] or 'BOM' in metadata['domain'] or 'Routing' in metadata['domain']:
        metadata['dataType'] = 'Master Data'
    else:
        metadata['dataType'] = 'Transactional Data'

    # Source
    metadata['source'] = 'ACE Rules'

    return metadata

# Process all rules
rules_dir = 'rules'
all_rules = []

for rule_folder in sorted(os.listdir(rules_dir)):
    rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')
    if os.path.isfile(rule_path):
        metadata = extract_metadata_final(rule_path)
        if metadata:
            all_rules.append(metadata)

# Save
output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Updated {len(all_rules)} rules with improved extraction\n")

# Show samples and stats
print("Sample rules:")
for i, rule in enumerate(all_rules[:8], 1):
    print(f"\n{i}. {rule['name']}")
    print(f"   Domain: {rule.get('domain')}")
    print(f"   Tables: {', '.join(rule.get('tables', [])) if rule.get('tables') else 'N/A'}")
    print(f"   Fields: {len(rule.get('fields', []))} fields")

# Domain distribution
domains = {}
for rule in all_rules:
    d = rule.get('domain')
    domains[d] = domains.get(d, 0) + 1

print("\n\nDomain Distribution:")
for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")
