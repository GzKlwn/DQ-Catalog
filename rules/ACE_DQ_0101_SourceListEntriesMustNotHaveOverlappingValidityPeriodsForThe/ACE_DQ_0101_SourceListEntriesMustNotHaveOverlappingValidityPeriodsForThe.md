# DQ Rule: ACE_00101 - Source list entries MUST NOT have overlapping validity periods for the same material, plant, and supplier.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00101 |
| Rule Name | Source list entries MUST NOT have overlapping validity periods for the same material, plant, and supplier. |
| Rule Name Score | 100% |
| Data Domain | Material Master |
| Object Type | Master |
| Business Process | Data Governance |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 10100 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00101_System_001_EORD_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: source list entries must not have overlapping validity periods for the same material, plant, and supplier.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** MARA
- **Related Tables:** MARC
- **Domain:** Material Master
- **Scope:** All active records in MARA
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from MARA that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in MARA, evaluates the defined error conditions: source list entries must not have overlapping validity periods for the same material, plant, and supplier.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields (Mandatory)
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 1 | zSourceSystemID | EORD.zSourceSystemID | | | | Yes |
| 2 | zConcatenatedKey | | Calculated | | Concatenate key fields | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived from Logic | |
| 4 | zDomainSegment | EORD.zSourceSystemID | | | | |

---

## SQL Implementation

### OptSel View
```sql
-- Rule ID: ACE_00101
-- Generated View: DQ_ACE00101_System_001_EORD_OptSel
-- Purpose: Return all candidate rows with per-row error flag (OptSel)

SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (WITH scoped AS (SELECT DISTINCT base.MANDT, base.MATNR, base.WERKS, base.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') base WHERE NULLIF(LTRIM(RTRIM(base.BDATU), '') IN ('29991231','20261231','20270630','20270730','20270331','20270131','29990327','20990331','20991130','99991231')) SELECT DISTINCT e1.MANDT, e1.MATNR, e1.WERKS, e1.ZEORD FROM [WRKDQ].[dbo].[EORD] e1 INNER JOIN scoped s ON e1.MANDT = s.MANDT AND e1.MATNR = s.MATNR AND e1.WERKS = s.WERKS AND e1.ZEORD = s.ZEORD) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU= '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD
```

### RptSel View
```sql
-- Rule ID: ACE_00101
-- Generated View: DQ_ACE00101_System_001_EORD_RptSel
-- Purpose: Return only error records from OptSel (RptSel)

SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (WITH scoped AS (SELECT DISTINCT base.MANDT, base.MATNR, base.WERKS, base.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '' UNION SELECT MANDT, MATNR, WERKS, ZEORD, BDATU FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') base WHERE NULLIF(LTRIM(RTRIM(base.BDATU), '') IN ('29991231','20261231','20270630','20270730','20270331','20270131','29990327','20990331','20991130','99991231')) SELECT DISTINCT e1.MANDT, e1.MATNR, e1.WERKS, e1.ZEORD FROM [WRKDQ].[dbo].[EORD] e1 INNER JOIN scoped s ON e1.MANDT = s.MANDT AND e1.MATNR = s.MATNR AND e1.WERKS = s.WERKS AND e1.ZEORD = s.ZEORD WHERE EXISTS (SELECT 1 FROM [WRKDQ].[dbo].[EORD] e2 WHERE e2.MANDT = e1.MANDT AND e2.MATNR = e1.MATNR AND e2.WERKS = e1.WERKS AND e2.LIFNR = e1.LIFNR AND e2.ZEORD <> e1.ZEORD AND e1.VDATU <= e2.BDATU AND e2.VDATU <= e1.BDATU)) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU= '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD
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
