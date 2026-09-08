import os
import re
import json

def rebuild_metadata_from_title_only(rule_path, folder_name):
    """
    Rebuild metadata using ONLY the markdown title (which is correct).
    Infer domain and other info from the title itself.
    """
    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None

    metadata = {}

    # Extract EXACT title from markdown (AUTHORITATIVE)
    title_match = re.search(r'^# DQ Rule: ACE_(\d+) - (.+?)$', content, re.MULTILINE)
    if not title_match:
        return None

    exact_title = title_match.group(2)
    metadata['name'] = folder_name

    # Infer domain from title keywords
    domain_keywords = {
        'BOM': 'Bill of Materials',
        'Material': 'Material Master',
        'Equipment': 'Equipment Master',
        'Address': 'Business Partner Master',
        'Business Partner': 'Business Partner Master',
        'Customer': 'Customer Master',
        'Vendor': 'Vendor Master',
        'Sales Order': 'Sales Orders',
        'Delivery': 'Delivery Headers',
        'Billing': 'Billing Documents',
        'Invoice': 'Billing Documents',
        'Purchase Order': 'Purchase Orders',
        'Requisition': 'Purchase Requisitions',
        'Internal Order': 'Internal Orders',
        'Inspection': 'Inspection Lots',
        'Quality': 'Quality Management',
        'Routing': 'Routing',
        'Pricing': 'Pricing Records',
        'Cost': 'Costing',
        'Costing': 'Costing',
        'Accounting': 'Accounting Documents',
        'Inventory': 'Physical Inventory',
        'Storage': 'Storage Bins',
        'Transport': 'Transportation',
        'Project': 'Project Master',
        'Hierarchy': 'Master Data',
        'Characteristic': 'Characteristics',
        'Functional Location': 'Internal Orders',
        'Maintenance': 'Internal Orders',
        'Task List': 'Routing',
        'Production': 'Production Planning',
        'Work Center': 'Production Planning',
    }

    detected_domain = 'Master Data'
    for keyword, domain in domain_keywords.items():
        if keyword.lower() in exact_title.lower():
            detected_domain = domain
            break

    metadata['domain'] = detected_domain

    # Extract tables based on domain
    domain_to_tables = {
        'Bill of Materials': ['MAST', 'STKO', 'STPO'],
        'Material Master': ['MARA', 'MARC'],
        'Equipment Master': ['EQUI', 'EQKT'],
        'Business Partner Master': ['BUT020', 'ADRC'],
        'Customer Master': ['KNA1', 'KNVV'],
        'Vendor Master': ['LFA1', 'LFB1'],
        'Sales Orders': ['VBAK', 'VBAP'],
        'Delivery Headers': ['LIKP', 'LIPS'],
        'Billing Documents': ['VBRK', 'VBRP'],
        'Purchase Orders': ['EKKO', 'EKPO'],
        'Purchase Requisitions': ['EBAN'],
        'Internal Orders': ['AUFM', 'AUFK'],
        'Inspection Lots': ['QAMR', 'QALS'],
        'Quality Management': ['A017'],
        'Routing': ['ROUT'],
        'Pricing Records': ['KONV'],
        'Costing': ['MKAL', 'CRCA'],
        'Accounting Documents': ['BKPF', 'BSEG'],
        'Physical Inventory': ['MKPF', 'MSEG'],
        'Storage Bins': ['LAGP'],
        'Transportation': ['VTTK'],
        'Project Master': ['PROJ', 'PRPS'],
        'Characteristics': ['CABN'],
        'Production Planning': ['AFKO', 'PLKO'],
    }

    metadata['tables'] = domain_to_tables.get(detected_domain, [])

    # Create meaningful description from title
    description = f"Validates that {exact_title.lower().replace('must', '').strip()}"
    if not description.endswith('.'):
        description += '.'

    metadata['description'] = description

    # Determine object type from domain
    metadata['object'] = 'Master' if 'Master' in detected_domain else 'Transactional'

    # Criticality (default High for ACE rules)
    criticality_match = re.search(r'\| Business Impact \| ([^|]+) \|', content)
    if criticality_match:
        impact = criticality_match.group(1).strip()
        metadata['criticality'] = impact
    else:
        metadata['criticality'] = 'High'

    # Industries based on domain
    industries = set()

    mfg_domains = ['Bill of Materials', 'Material Master', 'Equipment Master', 'Sales Orders', 'Delivery', 'Purchase Orders', 'Purchase Requisitions', 'Internal Orders', 'Inspection Lots', 'Quality', 'Routing', 'Production Planning', 'Physical Inventory', 'Storage Bins', 'Transportation']

    fin_domains = ['Billing Documents', 'Accounting Documents', 'Costing', 'Pricing Records']

    if any(d in detected_domain for d in mfg_domains):
        industries.add('Manufacturing')

    if any(d in detected_domain for d in fin_domains):
        industries.add('Finance')

    # Default if unclear
    if not industries:
        industries = {'Manufacturing', 'Finance'}

    metadata['industries'] = sorted(list(industries))

    # DataType
    metadata['dataType'] = 'Master Data' if 'Master' in detected_domain else 'Transactional Data'

    # Fields (default to empty since source files are corrupted)
    metadata['fields'] = []

    # Source
    metadata['source'] = 'ACE Rules'

    return metadata

# Process all rules
rules_dir = 'rules'
all_rules = []

print("Rebuilding metadata from rule titles only...\n")

for rule_folder in sorted(os.listdir(rules_dir)):
    rule_path = os.path.join(rules_dir, rule_folder, f'{rule_folder}.md')
    if os.path.isfile(rule_path) and rule_folder.startswith('ACE_DQ_'):
        metadata = rebuild_metadata_from_title_only(rule_path, rule_folder)
        if metadata:
            all_rules.append(metadata)

# Add the original 2 rules
original_rules = [
    {
        "name": "payment-terms-favorable",
        "tables": ["KNA1", "KNB1", "T001", "T052"],
        "fields": ["KUNNR", "ZTERM", "BUKRS"],
        "domain": "Customer Master",
        "object": "Master",
        "criticality": "Medium",
        "description": "Validates that customers do not have payment terms more favorable than the master data standard.",
        "industries": ["Finance", "Manufacturing"],
        "dataType": "Master Data",
        "source": "ACE Rules"
    },
    {
        "name": "invoice-credit-block",
        "tables": ["KNA1", "VBRK"],
        "fields": ["KUNNR", "VBELN", "BUKRS"],
        "domain": "Billing Documents",
        "object": "Transactional",
        "criticality": "Medium",
        "description": "Ensures invoices are not issued to customers with active credit blocks.",
        "industries": ["Finance"],
        "dataType": "Transactional Data",
        "source": "ACE Rules"
    }
]

all_rules.extend(original_rules)

# Save
output = {'rules': sorted(all_rules, key=lambda x: x['name'])}
with open('metadata.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Regenerated metadata.json with {len(all_rules)} rules")

# Statistics
domains = {}
for rule in all_rules:
    d = rule['domain']
    domains[d] = domains.get(d, 0) + 1

print("\nDomain Distribution:")
for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:10]:
    print(f"  - {domain}: {count} rules")

# Show samples
print("\nSample corrected rules:")
for rule in all_rules[:3]:
    print(f"\n{rule['name']}")
    print(f"  Domain: {rule['domain']}")
    print(f"  Tables: {', '.join(rule['tables'])}")
    print(f"  Description: {rule['description'][:70]}")
    print(f"  Source: {rule['source']}")
