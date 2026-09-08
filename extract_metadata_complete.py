import os
import json
import re

def extract_metadata_complete(rule_path):
    """
    Complete metadata extraction with comprehensive SAP table mapping
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

    # COMPREHENSIVE SAP Table to Domain mapping
    table_domain = {
        # Business Partner Master
        'ADRC': 'Business Partner Master',
        'BUT020': 'Business Partner Master',
        'BUT000': 'Business Partner Master',
        'BUT050': 'Business Partner Master',
        'BUT100': 'Business Partner Master',
        'BUTXT': 'Business Partner Master',
        'BPGE': 'Business Partner Master',
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
        # Production Planning
        'AFKO': 'Production Planning',
        'AFPO': 'Production Planning',
        'PLKO': 'Production Planning',
        'PLFL': 'Production Planning',
        'MAPL': 'Production Planning',
        'KAKO': 'Production Planning',
        # Inspection
        'A017': 'Inspection Plans',
        'QAMR': 'Inspection Lots',
        'QAPE': 'Inspection Lots',
        'QALS': 'Inspection Lots',
        'QMAT': 'Inspection Lots',
        'IFLOT': 'Inspection Lots',
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
        'KOAP': 'Pricing Records',
        # Purchase Orders
        'EKKO': 'Purchase Orders',
        'EKPO': 'Purchase Orders',
        'EKBE': 'Purchase Order History',
        # Purchase Requisitions
        'EBAN': 'Purchase Requisitions',
        'EINA': 'Purchase Requisitions',
        'EORD': 'Purchase Requisitions',
        # Reservations
        'RESB': 'Reservations',
        'RESA': 'Reservations',
        # Accounting
        'BKPF': 'Accounting Documents',
        'BSEG': 'Accounting Documents',
        'BSAK': 'Accounting Documents',
        'BSAS': 'Accounting Documents',
        # Costing / Product Costing
        'MKAL': 'Costing',
        'COEP': 'Costing',
        'COSP': 'Costing',
        'KEKO': 'Costing',
        'CRCA': 'Costing',
        'CRCO': 'Costing',
        'CRHD': 'Costing',
        'IMPTT': 'Costing',
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
        # Transportation/Freight
        'VTTK': 'Transportation',
        'VTTP': 'Transportation',
        'VTTS': 'Transportation',
        # Quality Management
        'CABN': 'Quality Management',
        'OBJK': 'Quality Management',
        'MHIS': 'Quality Management',
        # Characteristics/Configuration
        'CABN': 'Characteristics',
        'SETHEADER': 'Characteristics',
        'IKPF': 'Characteristics',
        # Procurement Card
        'EKAB': 'Purchase Orders',
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

    # Industries from Business Process
    process_match = re.search(r'\|\s*Business Process\s*\|\s*([^|]+)\s*\|', content)
    industries = set()

    if process_match:
        process = process_match.group(1).strip()
        # Manufacturing domain processes
        mfg_keywords = ['Sales', 'Order', 'Delivery', 'Procurement', 'Purchase', 'Vendor', 'Production', 'BOM', 'Routing', 'Quality', 'Inspection', 'Maintenance', 'Equipment', 'Material', 'Inventory', 'Transportation', 'Planning']
        if any(kw in process for kw in mfg_keywords):
            industries.add('Manufacturing')

        # Finance domain processes
        fin_keywords = ['Finance', 'Accounting', 'Payable', 'Receivable', 'Billing', 'Costing', 'Cost', 'Budget', 'GL', 'AP', 'AR']
        if any(kw in process for kw in fin_keywords):
            industries.add('Finance')

    # Default by domain if no industries detected
    if not industries:
        if any(kw in metadata['domain'] for kw in ['Sales', 'Order', 'Equipment', 'Material', 'BOM', 'Routing', 'Production', 'Inspection', 'Internal', 'Transportation', 'Delivery', 'Quality', 'Procurement', 'Purchase', 'Requisition']):
            industries.add('Manufacturing')
        if any(kw in metadata['domain'] for kw in ['Billing', 'Accounting', 'Costing']):
            industries.add('Finance')

    if not industries:
        industries = {'Manufacturing', 'Finance'}

    metadata['industries'] = sorted(list(industries))

    # DataType
    if 'Master' in metadata['domain'] or 'BOM' in metadata['domain'] or 'Routing' in metadata['domain'] or 'Planning' in metadata['domain']:
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
        metadata = extract_metadata_complete(rule_path)
        if metadata:
            all_rules.append(metadata)

# Save
output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Successfully extracted metadata for {len(all_rules)} rules\n")
print("=" * 80)
print("FINAL METADATA EXTRACTION REPORT")
print("=" * 80)

# Domain distribution
domains = {}
for rule in all_rules:
    d = rule.get('domain')
    domains[d] = domains.get(d, 0) + 1

print("\nDomain Distribution (sorted by frequency):")
print("-" * 80)
for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
    print(f"  {domain:<40} {count:>3} rules")

# Criticality distribution
print("\nCriticality Distribution:")
print("-" * 80)
criticalities = {}
for rule in all_rules:
    c = rule.get('criticality')
    criticalities[c] = criticalities.get(c, 0) + 1

for crit in ['High', 'Medium', 'Low']:
    count = criticalities.get(crit, 0)
    if count > 0:
        print(f"  {crit:<40} {count:>3} rules")

# DataType distribution
print("\nData Type Distribution:")
print("-" * 80)
datatypes = {}
for rule in all_rules:
    dt = rule.get('dataType')
    datatypes[dt] = datatypes.get(dt, 0) + 1

for dt in ['Master Data', 'Transactional Data']:
    count = datatypes.get(dt, 0)
    if count > 0:
        print(f"  {dt:<40} {count:>3} rules")

# Industry distribution
print("\nIndustry Coverage:")
print("-" * 80)
industries = {}
for rule in all_rules:
    for ind in rule.get('industries', []):
        industries[ind] = industries.get(ind, 0) + 1

for ind in sorted(industries.keys()):
    print(f"  {ind:<40} {industries[ind]:>3} rules")

print("\n" + "=" * 80)
print(f"Metadata file updated: metadata.json")
print(f"Total rules: {len(all_rules)}")
print(f"All rules include: name, tables, fields, domain, object, criticality,")
print(f"                  description, industries, dataType, source")
print("=" * 80)
