# DQ Rule: ACE_00104 - Finite-scheduling work centers MUST have an available-capacity end time later than the start time.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00104 |
| Rule Name | Finite-scheduling work centers MUST have an available-capacity end time later than the start time. |
| Rule Name Score | 100% |
| Data Domain | Production Planning |
| Object Type | Master |
| Business Process | Data Governance |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 10400 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00104_System_001_CRHD_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: finite-scheduling work centers must have an available-capacity end time later than the start time.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** AFKO
- **Related Tables:** PLKO
- **Domain:** Production Planning
- **Scope:** All active records in AFKO
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from AFKO that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in AFKO, evaluates the defined error conditions: finite-scheduling work centers must have an available-capacity end time later than the start time.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields (Mandatory)
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 1 | zSourceSystemID | CRHD.zSourceSystemID | | | | Yes |
| 2 | zConcatenatedKey | | Calculated | | Concatenate key fields | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived from Logic | |
| 4 | zDomainSegment | CRHD.zSourceSystemID | | | | |

---

## SQL Implementation

### OptSel View
```sql
-- Rule ID: ACE_00104
-- Generated View: DQ_ACE00104_System_001_CRHD_OptSel
-- Purpose: Return all candidate rows with per-row error flag (OptSel)

SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[KAKO] k ON h.MANDT = k.MANDT AND h.KAPID = k.KAPID WHERE h.XSPRR <> 'X' AND k.WERKS = h.WERKS AND k.KAPTER = 'X' AND NULLIF(LTRIM(RTRIM(h.FORTN), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE ENDDA >= '20250803' AND BEGDA <= '20250803' AND XSPRR <> 'X') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[CRCA] a ON h.MANDT = a.MANDT AND h.OBJTY = a.OBJTY AND h.OBJID = a.OBJID WHERE h.XSPRR <> 'X' AND a.ENDDA >= '20250803' AND a.BEGDA <= '20250803') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[CRCO] c ON h.MANDT = c.MANDT AND h.OBJTY = c.OBJTY AND h.OBJID = c.OBJID WHERE h.XSPRR <> 'X' AND c.ENDDA >= '20250803' AND c.BEGDA <= '20250803' AND c.KOSTL IS NOT NULL AND c.KOSTL <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h WHERE h.XSPRR <> 'X' AND (h.XTERM = 'X' OR h.XKOST = 'X' OR h.XDEFA = 'X')) AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[KAKO] k ON h.MANDT = k.MANDT AND h.KAPID = k.KAPID WHERE h.XSPRR <> 'X' AND k.WERKS = h.WERKS AND k.KAPTER = 'X') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID
```

### RptSel View
```sql
-- Rule ID: ACE_00104
-- Generated View: DQ_ACE00104_System_001_CRHD_RptSel
-- Purpose: Return only error records from OptSel (RptSel)

SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[KAKO] k ON h.MANDT = k.MANDT AND h.KAPID = k.KAPID WHERE h.XSPRR <> 'X' AND k.WERKS = h.WERKS AND k.KAPTER = 'X' AND NULLIF(LTRIM(RTRIM(h.FORTN), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004') AND k.ENDZT <= k.BEGZT) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE ENDDA >= '20250803' AND BEGDA <= '20250803' AND XSPRR <> 'X') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[CRCA] a ON h.MANDT = a.MANDT AND h.OBJTY = a.OBJTY AND h.OBJID = a.OBJID WHERE h.XSPRR <> 'X' AND a.ENDDA >= '20250803' AND a.BEGDA <= '20250803') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[CRCO] c ON h.MANDT = c.MANDT AND h.OBJTY = c.OBJTY AND h.OBJID = c.OBJID WHERE h.XSPRR <> 'X' AND c.ENDDA >= '20250803' AND c.BEGDA <= '20250803' AND c.KOSTL IS NOT NULL AND c.KOSTL <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h WHERE h.XSPRR <> 'X' AND (h.XTERM = 'X' OR h.XKOST = 'X' OR h.XDEFA = 'X')) AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID UNION SELECT violations.MANDT, violations.OBJTY, violations.OBJID FROM (SELECT DISTINCT h.MANDT, h.OBJTY, h.OBJID FROM [WRKDQ].[dbo].[CRHD] h INNER JOIN [WRKDQ].[dbo].[KAKO] k ON h.MANDT = k.MANDT AND h.KAPID = k.KAPID WHERE h.XSPRR <> 'X' AND k.WERKS = h.WERKS AND k.KAPTER = 'X') AS violations INNER JOIN (SELECT DISTINCT MANDT, OBJTY, OBJID FROM [WRKDQ].[dbo].[CRHD] WHERE NULLIF(LTRIM(RTRIM("FORTN"), '') IN ('ZPE002', 'ZPE003', 'SAP004', 'SAPPD1', 'SAP002', 'ZPE004')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.OBJTY = relevant.OBJTY AND violations.OBJID = relevant.OBJID
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
