import os
import re

def fix_sql_comments(rule_path):
    """Fix SQL comments to match markdown titles exactly"""

    try:
        with open(rule_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False

    # Extract the exact title from markdown
    title_match = re.search(r'^# DQ Rule: ACE_(\d+) - (.+?)$', content, re.MULTILINE)
    if not title_match:
        return False

    rule_num = title_match.group(1)
    exact_title = title_match.group(2)

    # Replace ALL SQL comments with the exact title
    # For OptSel
    content = re.sub(
        r'(-- ={60}\s+-- DQ Rule: ).*?(\n)',
        rf'\1{exact_title}\2',
        content
    )

    # Alternative pattern without the = signs
    content = re.sub(
        r'-- DQ Rule: [^\n]+',
        f'-- DQ Rule: {exact_title}',
        content
    )

    # Also fix Rule ID to match
    content = re.sub(
        r'-- Rule ID: ACE_\d+',
        f'-- Rule ID: ACE_{rule_num}',
        content
    )

    # Also fix the Rule Name in header to match title exactly
    content = re.sub(
        r'\| Rule Name \| [^|]+ \|',
        f'| Rule Name | {exact_title} |',
        content
    )

    try:
        with open(rule_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

# Process all rules
rules_dir = 'rules'
fixed = 0

for folder in sorted(os.listdir(rules_dir)):
    if folder.startswith('ACE_DQ_'):
        rule_path = os.path.join(rules_dir, folder, f'{folder}.md')
        if os.path.isfile(rule_path):
            if fix_sql_comments(rule_path):
                fixed += 1

print(f"Fixed SQL comments and rule names for {fixed} rules")
print("All titles, SQL comments, and headers now aligned")
