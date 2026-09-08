# DQ Rule: ACE_00100 - Agreement-linked source approvals MUST reference an agreement item for the same plant.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00100 |
| Rule Name | Agreement-linked source approvals MUST reference an agreement item for the same plant. |
| Rule Name Score | 100% |
| Data Domain | Master Data |
| Object Type | Master |
| Business Process | Data Governance |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 10000 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00100_System_001_EORD_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: agreement-linked source approvals must reference an agreement item for the same plant.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** UNKNOWN
- **Related Tables:** N/A
- **Domain:** Master Data
- **Scope:** All active records in UNKNOWN
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from UNKNOWN that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in UNKNOWN, evaluates the defined error conditions: agreement-linked source approvals must reference an agreement item for the same plant.. Flags records that violate the rule requirements.

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
-- Rule ID: ACE_00100
-- Generated View: DQ_ACE00100_System_001_EORD_OptSel
-- Purpose: Return all candidate rows with per-row error flag (OptSel)

SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (WITH relevant AS (SELECT DISTINCT src.MANDT, src.MATNR, src.WERKS, src.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU = '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') src INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231','20261231','20270630','20270730','20270331','20270131','29990327','20990331','20991130','99991231')) scope_filter ON src.MANDT = scope_filter.MANDT AND src.MATNR = scope_filter.MATNR AND src.WERKS = scope_filter.WERKS AND src.ZEORD = scope_filter.ZEORD) SELECT DISTINCT [WRKDQ].[dbo].[EORD].MANDT, [WRKDQ].[dbo].[EORD].MATNR, [WRKDQ].[dbo].[EORD].WERKS, [WRKDQ].[dbo].[EORD].ZEORD FROM [WRKDQ].[dbo].[EORD] INNER JOIN relevant ON [WRKDQ].[dbo].[EORD].MANDT = relevant.MANDT AND [WRKDQ].[dbo].[EORD].MATNR = relevant.MATNR AND [WRKDQ].[dbo].[EORD].WERKS = relevant.WERKS AND [WRKDQ].[dbo].[EORD].ZEORD = relevant.ZEORD INNER JOIN [WRKDQ].[dbo].[EKPO] ON [WRKDQ].[dbo].[EKPO].MANDT = [WRKDQ].[dbo].[EORD].MANDT AND [WRKDQ].[dbo].[EKPO].EBELN = [WRKDQ].[dbo].[EORD].EBELN AND [WRKDQ].[dbo].[EKPO].EBELP = [WRKDQ].[dbo].[EORD].EBELP WHERE NULLIF(LTRIM(RTRIM([WRKDQ].[dbo].[EORD].EBELN), '') IS NOT NULL) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU= '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD
```

### RptSel View
```sql
-- Rule ID: ACE_00100
-- Generated View: DQ_ACE00100_System_001_EORD_RptSel
-- Purpose: Return only error records from OptSel (RptSel)

SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (WITH relevant AS (SELECT DISTINCT src.MANDT, src.MATNR, src.WERKS, src.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU = '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '' UNION SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') src INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231','20261231','20270630','20270730','20270331','20270131','29990327','20990331','20991130','99991231')) scope_filter ON src.MANDT = scope_filter.MANDT AND src.MATNR = scope_filter.MATNR AND src.WERKS = scope_filter.WERKS AND src.ZEORD = scope_filter.ZEORD) SELECT DISTINCT [WRKDQ].[dbo].[EORD].MANDT, [WRKDQ].[dbo].[EORD].MATNR, [WRKDQ].[dbo].[EORD].WERKS, [WRKDQ].[dbo].[EORD].ZEORD FROM [WRKDQ].[dbo].[EORD] INNER JOIN relevant ON [WRKDQ].[dbo].[EORD].MANDT = relevant.MANDT AND [WRKDQ].[dbo].[EORD].MATNR = relevant.MATNR AND [WRKDQ].[dbo].[EORD].WERKS = relevant.WERKS AND [WRKDQ].[dbo].[EORD].ZEORD = relevant.ZEORD INNER JOIN [WRKDQ].[dbo].[EKPO] ON [WRKDQ].[dbo].[EKPO].MANDT = [WRKDQ].[dbo].[EORD].MANDT AND [WRKDQ].[dbo].[EKPO].EBELN = [WRKDQ].[dbo].[EORD].EBELN AND [WRKDQ].[dbo].[EKPO].EBELP = [WRKDQ].[dbo].[EORD].EBELP WHERE NULLIF(LTRIM(RTRIM([WRKDQ].[dbo].[EORD].EBELN), '') IS NOT NULL AND [WRKDQ].[dbo].[EKPO].WERKS <> [WRKDQ].[dbo].[EORD].WERKS) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU = '20260803' AND BDATU= '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE BDATU BETWEEN '20260803' AND '20270803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE VDATU BETWEEN '20250803' AND '20260803') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE EBELN IS NOT NULL AND EBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD UNION SELECT violations.MANDT, violations.MATNR, violations.WERKS, violations.ZEORD FROM (SELECT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE AUTET IS NOT NULL AND AUTET <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, MATNR, WERKS, ZEORD FROM [WRKDQ].[dbo].[EORD] WHERE NULLIF(LTRIM(RTRIM("BDATU"), '') IN ('29991231', '20261231', '20270630', '20270730', '20270331', '20270131', '29990327', '20990331', '20991130', '99991231')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.MATNR = relevant.MATNR AND violations.WERKS = relevant.WERKS AND violations.ZEORD = relevant.ZEORD
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
