# DQ Rule: ACE_00102 - Task lists MUST include at least one maintained operation.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00102 |
| Rule Name | Task lists MUST include at least one maintained operation. |
| Rule Name Score | 100% |
| Data Domain | Routing |
| Object Type | Master |
| Business Process | Data Governance |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 10200 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00102_System_001_PLKO_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: task lists must include at least one maintained operation.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** ROUT
- **Related Tables:** N/A
- **Domain:** Routing
- **Scope:** All active records in ROUT
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from ROUT that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in ROUT, evaluates the defined error conditions: task lists must include at least one maintained operation.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields (Mandatory)
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 1 | zSourceSystemID | PLKO.zSourceSystemID | | | | Yes |
| 2 | zConcatenatedKey | | Calculated | | Concatenate key fields | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived from Logic | |
| 4 | zDomainSegment | PLKO.zSourceSystemID | | | | |

---

## SQL Implementation

### OptSel View
```sql
-- Rule ID: ACE_00102
-- Generated View: DQ_ACE00102_System_001_PLKO_OptSel
-- Purpose: Return all candidate rows with per-row error flag (OptSel)

SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (WITH relevant AS (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM (SELECT * FROM (SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (DELKZ IS NULL OR DELKZ = '') AND (REODAT = '00000000' OR REODAT IS NULL)) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLPO] o ON k.MANDT = o.MANDT AND k.PLNTY = o.PLNTY AND k.PLNNR = o.PLNNR WHERE o.LOEKZ_INHERITED IS NULL OR o.LOEKZ_INHERITED = '') AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[MAPL] m ON k.MANDT = m.MANDT AND k.PLNTY = m.PLNTY AND k.PLNNR = m.PLNNR AND k.PLNAL = m.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLFL] f ON k.MANDT = f.MANDT AND k.PLNTY = f.PLNTY AND k.PLNNR = f.PLNNR AND k.PLNAL = f.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (KTEXT IS NOT NULL AND KTEXT <> '') OR (VAGRP IS NOT NULL AND VAGRP <> '') OR (STRAT IS NOT NULL AND STRAT <> '')) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL) AS base)) SELECT r.MANDT, r.PLNTY, r.PLNNR, r.PLNAL, r.ZAEHL FROM relevant r) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (DELKZ IS NULL OR DELKZ = '') AND (REODAT = '00000000' OR REODAT IS NULL)) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLPO] o ON k.MANDT = o.MANDT AND k.PLNTY = o.PLNTY AND k.PLNNR = o.PLNNR WHERE o.LOEKZ_INHERITED IS NULL OR o.LOEKZ_INHERITED = '') AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[MAPL] m ON k.MANDT = m.MANDT AND k.PLNTY = m.PLNTY AND k.PLNNR = m.PLNNR AND k.PLNAL = m.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLFL] f ON k.MANDT = f.MANDT AND k.PLNTY = f.PLNTY AND k.PLNNR = f.PLNNR AND k.PLNAL = f.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (KTEXT IS NOT NULL AND KTEXT <> '') OR (VAGRP IS NOT NULL AND VAGRP <> '') OR (STRAT IS NOT NULL AND STRAT <> '')) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL
```

### RptSel View
```sql
-- Rule ID: ACE_00102
-- Generated View: DQ_ACE00102_System_001_PLKO_RptSel
-- Purpose: Return only error records from OptSel (RptSel)

SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (WITH relevant AS (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM (SELECT * FROM (SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (DELKZ IS NULL OR DELKZ = '') AND (REODAT = '00000000' OR REODAT IS NULL)) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLPO] o ON k.MANDT = o.MANDT AND k.PLNTY = o.PLNTY AND k.PLNNR = o.PLNNR WHERE o.LOEKZ_INHERITED IS NULL OR o.LOEKZ_INHERITED = '') AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[MAPL] m ON k.MANDT = m.MANDT AND k.PLNTY = m.PLNTY AND k.PLNNR = m.PLNNR AND k.PLNAL = m.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLFL] f ON k.MANDT = f.MANDT AND k.PLNTY = f.PLNTY AND k.PLNNR = f.PLNNR AND k.PLNAL = f.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (KTEXT IS NOT NULL AND KTEXT <> '') OR (VAGRP IS NOT NULL AND VAGRP <> '') OR (STRAT IS NOT NULL AND STRAT <> '')) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant_types ON violations.MANDT = relevant_types.MANDT AND violations.PLNTY = relevant_types.PLNTY AND violations.PLNNR = relevant_types.PLNNR AND violations.PLNAL = relevant_types.PLNAL AND violations.ZAEHL = relevant_types.ZAEHL) AS base)) SELECT r.MANDT, r.PLNTY, r.PLNNR, r.PLNAL, r.ZAEHL FROM relevant r WHERE NOT EXISTS (SELECT 1 FROM [WRKDQ].[dbo].[PLPO] o WHERE o.MANDT = r.MANDT AND o.PLNTY = r.PLNTY AND o.PLNNR = r.PLNNR AND (o.LOEKZ_INHERITED IS NULL OR o.LOEKZ_INHERITED = ''))) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (DELKZ IS NULL OR DELKZ = '') AND (REODAT = '00000000' OR REODAT IS NULL)) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLPO] o ON k.MANDT = o.MANDT AND k.PLNTY = o.PLNTY AND k.PLNNR = o.PLNNR WHERE o.LOEKZ_INHERITED IS NULL OR o.LOEKZ_INHERITED = '') AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[MAPL] m ON k.MANDT = m.MANDT AND k.PLNTY = m.PLNTY AND k.PLNNR = m.PLNNR AND k.PLNAL = m.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT DISTINCT k.MANDT, k.PLNTY, k.PLNNR, k.PLNAL, k.ZAEHL FROM [WRKDQ].[dbo].[PLKO] k INNER JOIN [WRKDQ].[dbo].[PLFL] f ON k.MANDT = f.MANDT AND k.PLNTY = f.PLNTY AND k.PLNNR = f.PLNNR AND k.PLNAL = f.PLNAL) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL UNION SELECT violations.MANDT, violations.PLNTY, violations.PLNNR, violations.PLNAL, violations.ZAEHL FROM (SELECT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE (KTEXT IS NOT NULL AND KTEXT <> '') OR (VAGRP IS NOT NULL AND VAGRP <> '') OR (STRAT IS NOT NULL AND STRAT <> '')) AS violations INNER JOIN (SELECT DISTINCT MANDT, PLNTY, PLNNR, PLNAL, ZAEHL FROM [WRKDQ].[dbo].[PLKO] WHERE NULLIF(LTRIM(RTRIM("PLNTY"), '') IN ('E', 'Q', '2', 'T', 'A', 'S')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.PLNTY = relevant.PLNTY AND violations.PLNNR = relevant.PLNNR AND violations.PLNAL = relevant.PLNAL AND violations.ZAEHL = relevant.ZAEHL
```

---

## Rule Quality Attributes

| Attribute | Value |
|---|---|
| Created Date | 2025-09-04 |
| Last Modified | 2025-09-04 |
| Review Status | Generated |
| DQ Scope | Complete |
| Rule Completeness | 100% |
