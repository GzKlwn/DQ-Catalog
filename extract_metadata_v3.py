import os
import json
import re

def extract_metadata_v3(rule_path):
    """
    Extract metadata with smart domain inference:
    1. Use Primary Table from scope to determine domain
    2. Use rule title for context clues
    3. Map Business Process to industry
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

    # Comprehensive SAP Table to Domain mapping - AUTHORITATIVE
    table_domain = {
        # Business Partner Master
        'ADRC': 'Business Partner Master',
        'BUT020': 'Business Partner Master',
        'BUT000': 'Business Partner Master',
        'BUT050': 'Business Partner Master',
        'BUT100': 'Business Partner Master',
        'BUTXT': 'Business Partner Master',
        # Customer Master
        'KNA1': 'Customer Master',
        'KNVV': 'Customer Master',
        'KNB1': 'Customer Master',
        'KNVP': 'Customer Master',
        # Vendor Master
        'LFA1': 'Vendor Master',
        'LFB1': 'Vendor Master',
        'LFBK': 'Vendor Master',
        # Material Master
        'MARA': 'Material Master',
        'MARC': 'Material Master',
        'MATS': 'Material Master',
        # Equipment Master
        'EQUI': 'Equipment Master',
        'EQKT': 'Equipment Master',
        'EQFP': 'Equipment Master',
        'AFIH': 'Equipment Master',
        'EQUZ': 'Equipment Master',
        'ILOA': 'Equipment Master',
        # Bill of Materials
        'MAST': 'Bill of Materials',
        'STKO': 'Bill of Materials',
        'STPO': 'Bill of Materials',
        'PLPO': 'Bill of Materials',
        # Routing
        'ROUT': 'Routing',
        'PLNT': 'Routing',
        # Inspection
        'A017': 'Inspection Plans',
        'QAMR': 'Inspection Lots',
        'QAPE': 'Inspection Lots',
        'QALS': 'Inspection Lots',
        # Internal Orders / Maintenance
        'AUFM': 'Internal Orders',
        'AFPO': 'Internal Orders',
        'AFRU': 'Internal Orders',
        'AUFK': 'Internal Orders',
        # Sales Orders
        'VBAK': 'Sales Orders',
        'VBAP': 'Sales Orders',
        'VBAS': 'Sales Orders',
        # Deliveries
        'LIKP': 'Delivery Headers',
        'LIPS': 'Delivery Items',
        # Billing
        'VBRK': 'Billing Documents',
        'VBRP': 'Billing Documents',
        # Pricing/Conditions
        'KONV': 'Pricing Records',
        'KONH': 'Pricing Records',
        # Purchase Orders
        'EKKO': 'Purchase Orders',
        'EKPO': 'Purchase Orders',
        'EKBE': 'Purchase Order History',
        # Reservations
        'RESB': 'Reservations',
        'RESA': 'Reservations',
        # Accounting
        'BKPF': 'Accounting Documents',
        'BSEG': 'Accounting Documents',
        'BSAK': 'Accounting Documents',
        'BSAS': 'Accounting Documents',
        # Costing
        'MKAL': 'Costing',
        'COEP': 'Costing',
        'COSP': 'Costing',
        # Physical Inventory
        'MKPF': 'Physical Inventory',
        'MSEG': 'Physical Inventory',
        'MSLB': 'Physical Inventory',
        # Storage
        'LAGP': 'Storage Bins',
        'LQUA': 'Storage Bins',
        # Project
        'PROJ': 'Project Master',
        'PRPS': 'Project Master',
        'PRCT': 'Project Master',
        'PRBU': 'Project Master',
    }

    # Extract tables from scope section
    tables_set = set()
    scope_pattern = r'### 2\. Specific Relevancy Criteria/Scope.*?(?=\n###|\n---)'
    scope_match = re.search(scope_pattern, content, re.DOTALL)

    if scope_match:
        scope_section = scope_match.group(0)
        # Look for "Primary Table:" or "Related Tables:"
        primary_table_match = re.search(r'\*\*Primary Table:\*\*\s*([A-Z_0-9]+)', scope_section)
        if primary_table_match:
            tables_set.add(primary_table_match.group(1))

        # Look for related tables
        related_tables_match = re.search(r'\*\*Related Tables:\*\*\s*([A-Z_0-9, ]+)', scope_section)
        if related_tables_match:
            for table in related_tables_match.group(1).split(','):
                t = table.strip()
                if t and t.isupper():
                    tables_set.add(t)

    # Fallback: extract from SQL FROM/JOIN
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
            if field not in ['CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'SELECT']:
                fields_set.add(field)

    metadata['fields'] = sorted(list(fields_set))

    # Extract domain: use primary table mapping
    if metadata['tables']:
        # Use the first table (primary) to map to domain
        primary_table = metadata['tables'][0]
        metadata['domain'] = table_domain.get(primary_table, 'Master Data')
    else:
        # Try from Data Domain header (if not generic)
        domain_match = re.search(r'\|\s*Data Domain\s*\|\s*([^|]+)\s*\|', content)
        if domain_match:
            domain_raw = domain_match.group(1).strip()
            domain = domain_raw.split(',')[0].strip()
            if domain != 'Master Data':
                metadata['domain'] = domain
            else:
                metadata['domain'] = 'Master Data'
        else:
            metadata['domain'] = 'Master Data'

    # Object Type
    object_match = re.search(r'\|\s*Object Type\s*\|\s*([^|]+)\s*\|', content)
    metadata['object'] = object_match.group(1).strip() if object_match else 'Master'

    # Criticality from Business Impact
    impact_match = re.search(r'\|\s*Business Impact\s*\|\s*([^|]+)\s*\|', content)
    if impact_match:
        impact = impact_match.group(1).strip()
        metadata['criticality'] = {'High': 'High', 'Medium': 'Medium', 'Low': 'Low'}.get(impact, 'Medium')
    else:
        metadata['criticality'] = 'Medium'

    # Description from Functional/Business Description
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

    # Industries from Business Process
    process_match = re.search(r'\|\s*Business Process\s*\|\s*([^|]+)\s*\|', content)
    industries = set()

    if process_match:
        process = process_match.group(1).strip()
        # Manufacturing domain processes
        mfg_keywords = ['Sales', 'Order', 'Delivery', 'Procurement', 'Purchase', 'Vendor', 'Production', 'BOM', 'Routing', 'Quality', 'Inspection', 'Maintenance', 'Equipment', 'Material', 'Inventory']
        if any(kw in process for kw in mfg_keywords):
            industries.add('Manufacturing')

        # Finance domain processes
        fin_keywords = ['Finance', 'Accounting', 'Payable', 'Receivable', 'Billing', 'Costing', 'Cost', 'Budget', 'GL', 'AP', 'AR']
        if any(kw in process for kw in fin_keywords):
            industries.add('Finance')

    # If no industries detected, default based on domain
    if not industries:
        if 'Sales' in metadata['domain'] or 'Order' in metadata['domain'] or 'Equipment' in metadata['domain'] or 'Material' in metadata['domain'] or 'BOM' in metadata['domain']:
            industries.add('Manufacturing')
        if 'Billing' in metadata['domain'] or 'Accounting' in metadata['domain'] or 'Costing' in metadata['domain']:
            industries.add('Finance')

    if not industries:
        industries = {'Manufacturing', 'Finance'}

    metadata['industries'] = sorted(list(industries))

    # DataType
    if 'Master' in metadata['domain'] or 'BOM' in metadata['domain'] or 'Routing' in metadata['domain']:
        metadata['dataType'] = 'Master Data'
    else:
        metadata['dataType'] = 'Transactional Data'

    # Source
    metadata['source'] = 'ACE Rules'

    return metadata

# Main
rules_dir = 'rules'
all_rules = []

for rule_folder in sorted(os.listdir(rules_dir)):
    rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')
    if os.path.isfile(rule_path):
        metadata = extract_metadata_v3(rule_path)
        if metadata:
            all_rules.append(metadata)

# Save
output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Successfully extracted metadata for {len(all_rules)} rules\n")

# Statistics
print("=" * 80)
print("EXTRACTION RESULTS")
print("=" * 80)

# Show samples
print("\nSample Rules (First 10):")
for i, rule in enumerate(all_rules[:10], 1):
    print(f"\n{i}. {rule['name'][:60]}")
    print(f"   Domain: {rule.get('domain')}")
    print(f"   Tables: {', '.join(rule.get('tables', [])[:3])}")
    print(f"   Fields: {len(rule.get('fields', []))} fields")
    print(f"   Criticality: {rule.get('criticality')}")

# Domain distribution
domains = {}
for rule in all_rules:
    d = rule.get('domain')
    domains[d] = domains.get(d, 0) + 1

print("\n\nDomain Distribution (by frequency):")
for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")

# Criticality distribution
criticalities = {}
for rule in all_rules:
    c = rule.get('criticality')
    criticalities[c] = criticalities.get(c, 0) + 1

print("\n\nCriticality Distribution:")
for crit, count in sorted(criticalities.items(), key=lambda x: -x[1]):
    print(f"  {crit}: {count}")

# DataType distribution
datatypes = {}
for rule in all_rules:
    dt = rule.get('dataType')
    datatypes[dt] = datatypes.get(dt, 0) + 1

print("\n\nData Type Distribution:")
for dt, count in sorted(datatypes.items(), key=lambda x: -x[1]):
    print(f"  {dt}: {count}")

print("\n" + "=" * 80)
print("metadata.json updated successfully")
print("=" * 80)
