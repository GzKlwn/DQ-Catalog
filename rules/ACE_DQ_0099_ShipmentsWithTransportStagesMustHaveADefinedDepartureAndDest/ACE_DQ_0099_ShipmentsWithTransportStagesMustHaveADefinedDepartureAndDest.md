# DQ Rule: ACE_00099 - Shipments with transport stages MUST have a defined departure and destination reference for every stage.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00099 |
| Rule Name | Shipments with transport stages MUST have a defined departure and destination reference for every stage. |
| Rule Name Score | 100% |
| Data Domain | Transportation |
| Object Type | Master |
| Business Process | Data Governance |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 9900 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00099_System_001_VTTK_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: shipments with transport stages must have a defined departure and destination reference for every stage.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** VTTK
- **Related Tables:** N/A
- **Domain:** Transportation
- **Scope:** All active records in VTTK
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from VTTK that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in VTTK, evaluates the defined error conditions: shipments with transport stages must have a defined departure and destination reference for every stage.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields (Mandatory)
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 1 | zSourceSystemID | VTTK.zSourceSystemID | | | | Yes |
| 2 | zConcatenatedKey | | Calculated | | Concatenate key fields | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived from Logic | |
| 4 | zDomainSegment | VTTK.zSourceSystemID | | | | |

---

## SQL Implementation

### OptSel View
```sql
-- Rule ID: ACE_00099
-- Generated View: DQ_ACE00099_System_001_VTTK_OptSel
-- Purpose: Return all candidate rows with per-row error flag (OptSel)

SELECT violations.MANDT, violations.TKNUM FROM (WITH relevant_shipments AS (SELECT DISTINCT MANDT, TKNUM FROM (SELECT violations.MANDT, violations.TKNUM FROM (SELECT DISTINCT v.MANDT, v.TKNUM FROM [WRKDQ].[dbo].[VTTK] v INNER JOIN [WRKDQ].[dbo].[VTTP] i ON v.MANDT = i.MANDT AND v.TKNUM = i.TKNUM WHERE i.VBELN IS NOT NULL AND i.VBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE TDLNR IS NOT NULL AND TDLNR <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE ROUTE IS NOT NULL AND ROUTE <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM) AS base) SELECT DISTINCT s.MANDT, s.TKNUM FROM [WRKDQ].[dbo].[VTTS] s INNER JOIN relevant_shipments r ON s.MANDT = r.MANDT AND s.TKNUM = r.TKNUM) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.TKNUM FROM (SELECT DISTINCT v.MANDT, v.TKNUM FROM [WRKDQ].[dbo].[VTTK] v INNER JOIN [WRKDQ].[dbo].[VTTP] i ON v.MANDT = i.MANDT AND v.TKNUM = i.TKNUM WHERE i.VBELN IS NOT NULL AND i.VBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE TDLNR IS NOT NULL AND TDLNR <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE ROUTE IS NOT NULL AND ROUTE <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM
```

### RptSel View
```sql
-- Rule ID: ACE_00099
-- Generated View: DQ_ACE00099_System_001_VTTK_RptSel
-- Purpose: Return only error records from OptSel (RptSel)

SELECT violations.MANDT, violations.TKNUM FROM (WITH relevant_shipments AS (SELECT DISTINCT MANDT, TKNUM FROM (SELECT violations.MANDT, violations.TKNUM FROM (SELECT DISTINCT v.MANDT, v.TKNUM FROM [WRKDQ].[dbo].[VTTK] v INNER JOIN [WRKDQ].[dbo].[VTTP] i ON v.MANDT = i.MANDT AND v.TKNUM = i.TKNUM WHERE i.VBELN IS NOT NULL AND i.VBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE TDLNR IS NOT NULL AND TDLNR <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE ROUTE IS NOT NULL AND ROUTE <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM) AS base) SELECT DISTINCT s.MANDT, s.TKNUM FROM [WRKDQ].[dbo].[VTTS] s INNER JOIN relevant_shipments r ON s.MANDT = r.MANDT AND s.TKNUM = r.TKNUM WHERE (NULLIF(LTRIM(RTRIM(s.VSTEL), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.WERKA), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.LGORTA), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.KUNNA), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.BELAD), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.LGNUMA), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.ABORT01), '') IS NULL) OR (NULLIF(LTRIM(RTRIM(s.ADRNZ), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.WERKZ), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.LGORTZ), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.KUNNZ), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.ABLAD), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.KUNABLZ), '') IS NULL AND NULLIF(LTRIM(RTRIM(s.EDORT01), '') IS NULL)) AS violations INNER JOIN (SELECT * FROM (SELECT violations.MANDT, violations.TKNUM FROM (SELECT DISTINCT v.MANDT, v.TKNUM FROM [WRKDQ].[dbo].[VTTK] v INNER JOIN [WRKDQ].[dbo].[VTTP] i ON v.MANDT = i.MANDT AND v.TKNUM = i.TKNUM WHERE i.VBELN IS NOT NULL AND i.VBELN <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE TDLNR IS NOT NULL AND TDLNR <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM UNION SELECT violations.MANDT, violations.TKNUM FROM (SELECT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE ROUTE IS NOT NULL AND ROUTE <> '') AS violations INNER JOIN (SELECT DISTINCT MANDT, TKNUM FROM [WRKDQ].[dbo].[VTTK] WHERE NULLIF(LTRIM(RTRIM("SHTYP"), '') IN ('YPT0', 'ZSD7', 'YPT1', 'ZSD5', 'YWT0', 'YSN2', 'ZSD2', 'ZSD3', 'YWR0', 'ZSD6')) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM) AS base) AS relevant ON violations.MANDT = relevant.MANDT AND violations.TKNUM = relevant.TKNUM
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
