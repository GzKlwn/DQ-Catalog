# DQ Rule: A customer must not have payment terms more favorable than the master data standard

## Rule Header

### Rule

| Field | Value |
|-------|-------|
| SKP Rule ID | SKP_RULE_0006 |
| Rule Name | A customer must not have payment terms more favorable than the master data standard |
| Rule Name Score | 100% |
| Data Domain | Customer Master |
| Object Type | Master |
| Business Process | Cross-Process |
| Business Impact | Medium |
| Rule Type | Error |
| Source | Bespoke |

### Implementation

| Field | Value |
|-------|-------|
| DQOps ID | 0011 |
| System | `{SOURCE_SYSTEM}` (configured in Studio) |
| View Type |  |
| Generated View | `DQ_0011_{SOURCE_SYSTEM}_KNA1_ZTERM_Customer_Payment_Terms_More_Favorable_Master_OptSel` |

### Description

**1. Functional/Business Description**

Customers with payment terms more favorable than the master data standard create cash flow risk, margin erosion, and potential audit findings. Unauthorized deviations from corporate payment policies can signal fraud or governance failures.

**2. Specific Relevancy Criteria/Scope**

All active customer company code records (KNB1) with payment terms compared against standard master data terms.

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieve customer payment terms (KNB1.ZTERM) for all active customers not flagged for deletion in KNA1 or KNB1.

- **Check** <br /> Mark any record where:
  KNB1.ZTERM indicates more favorable payment terms than the organization's defined master data standard

- **Return** <br /> Records where customer payment terms exceed standard thresholds, indicating unauthorized favorable terms requiring review and correction.

## Output Fields

### Technical Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 1 | zSourceSystemID | KNA1.zSourceSystemID |  |  |  | Yes |
| 2 | zConcatenatedKey |  | Calculated |  | Concatenate: KNA1.zSourceSystemID + '_' + KNA1.KUNNR + '_' + KNB1.BUKRS | Yes |
| 3 | zIsErrorFlag |  | BIT (1/0) |  | Derived from Logic: 1 = fails DQ check (candidate), 0 = passes DQ check (compliant) |  |
| 9 | zDomainSegment | KNA1.zDomainSegment |  |  |  |  |

### Basic Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 4 | Customer Number | KNA1.KUNNR |  |  |  | Yes |
| 7 | Customer Name | KNA1.NAME1 |  |  |  |  |

### Organizational Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 5 | Company Code | KNB1.BUKRS |  |  |  |  |
| 6 | Payment Terms | KNB1.ZTERM |  |  |  |  |
| 8 | Company Name | T001.BUTXT |  |  |  |  |
| 10 | Company Standard Payment Terms | T001.ZTERM |  |  |  |  |

### Value Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 11 | Customer Payment Days | T052_CUST.ZBD1T |  |  |  |  |
| 12 | Standard Payment Days | T052_STD.ZBD1T |  |  |  |  |
| 13 | Days More Favorable | CASE WHEN T052_CUST.ZBD1T > T052_STD.ZBD1T THEN T052_CUST.ZBD1T - T052_STD.ZBD1T ELSE 0 END |  |  |  |  |

## Logic / Check Conditions

| Element | Operator | Table.Field | Value | Instruction |
|---------|----------|-------------|-------|-------------|
| Customer payment terms more favorable than standard | > T052_STD.ZBD1T | T052_CUST.ZBD1T |  |  |
| Customer has terms but no company standard defined | IS NULL | T052_STD.ZTERM |  |  |

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---------|--------|--------|------|-----|-------------|
| Customer → Company Code | KNA1 | KNB1 | LEFT JOIN | KUNNR=KUNNR AND KNA1.zSourceSystemID = KNB1.zSourceSystemID | 1:N |
| KNB1 -> T001 (Company Name) | KNB1 | T001 | LEFT JOIN | KNB1.BUKRS = T001.BUKRS AND KNB1.zSourceSystemID = T001.zSourceSystemID |  |
| T052 (Customer Terms) | KNB1 | T052 | LEFT | KNB1.zSourceSystemID = T052_CUST.zSourceSystemID AND KNB1.ZTERM = T052_CUST.ZTERM |  |
| T052 (Standard Terms) | T001 | T052 | LEFT | T001.zSourceSystemID = T052_STD.zSourceSystemID AND T001.ZTERM = T052_STD.ZTERM |  |

## Filters

### Inclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Limit to configured source system | = | KNA1 | zSourceSystemID | `{SOURCE_SYSTEM_ID}` (configured in Studio) |

### Exclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Exclude records flagged for deletion at KNA1 level | <> | KNA1 | LOEVM | 'X' |
| Exclude records flagged for deletion at KNB1 level | <> | KNB1 | LOEVM | 'X' |

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: A customer must not have payment terms more favorable than the master data standard
-- Rule ID: 0011
-- View: Opportunity Report (OptSel)
-- Target: MS SQL Server
-- ============================================================
-- NOTE: Replace {SOURCE_SYSTEM_ID} with the configured source system ID from Studio

CREATE VIEW [dbo].[DQ_0011_{SOURCE_SYSTEM}_KNA1_ZTERM_Customer_Payment_Terms_More_Favorable_Master_OptSel] AS
SELECT

 -- Syniti Technical Fields
 KNA1.zSourceSystemID AS [zSourceSystemID],
 CONCAT(KNA1.zSourceSystemID, '_', KNA1.KUNNR, '_', KNB1.BUKRS) AS [zConcatenatedKey],
 CASE
 /* Flag as error when customer payment terms allow more days than company standard */
 WHEN T052_CUST.ZBD1T > T052_STD.ZBD1T THEN 1
 /* Also flag if customer has terms but company has no standard defined (cannot validate) */
 WHEN KNB1.ZTERM IS NOT NULL
 AND LTRIM(RTRIM(KNB1.ZTERM)) <> ''
 AND T052_STD.ZTERM IS NULL THEN 1
 ELSE 0
 END AS [zIsErrorFlag],
 KNA1.zDomainSegment AS [zDomainSegment],

 -- Basic Fields
 KNA1.KUNNR AS [Customer Number],
 KNA1.NAME1 AS [Customer Name],

 -- Organizational Context
 KNB1.BUKRS AS [Company Code],
 T001.BUTXT AS [Company Name],
 KNB1.ZTERM AS [Customer Payment Terms],
 T001.ZTERM AS [Company Standard Payment Terms],

 -- Value Context
 T052_CUST.ZBD1T AS [Customer Payment Days],
 T052_STD.ZBD1T AS [Standard Payment Days],
 CASE
 WHEN T052_CUST.ZBD1T > T052_STD.ZBD1T
 THEN T052_CUST.ZBD1T - T052_STD.ZBD1T
 ELSE 0
 END AS [Days More Favorable]

FROM [WRKDQ].[dbo].[KNA1] AS KNA1

/* Join customer to company code data */
LEFT JOIN [WRKDQ].[dbo].[KNB1] AS KNB1
 ON KNA1.zSourceSystemID = KNB1.zSourceSystemID
 AND KNA1.KUNNR = KNB1.KUNNR

/* Join to company code master for company name and standard payment terms */
LEFT JOIN [WRKDQ].[dbo].[T001] AS T001
 ON KNB1.zSourceSystemID = T001.zSourceSystemID
 AND KNB1.BUKRS = T001.BUKRS

/* Join to payment terms config to get customer's actual payment days */
LEFT JOIN [WRKDQ].[dbo].[T052] AS T052_CUST
 ON KNB1.zSourceSystemID = T052_CUST.zSourceSystemID
 AND KNB1.ZTERM = T052_CUST.ZTERM

/* Join to payment terms config to get company standard payment days */
LEFT JOIN [WRKDQ].[dbo].[T052] AS T052_STD
 ON T001.zSourceSystemID = T052_STD.zSourceSystemID
 AND T001.ZTERM = T052_STD.ZTERM

WHERE
 /* Exclude records flagged for deletion at customer general level */
 ISNULL(KNA1.LOEVM, '') <> 'X'
 /* Exclude records flagged for deletion at company code level */
 AND ISNULL(KNB1.LOEVM, '') <> 'X'
 /* Limit to configured source system (replace {SOURCE_SYSTEM_ID} with Studio configuration) */
 AND KNA1.zSourceSystemID = '{SOURCE_SYSTEM_ID}'
;
```

## SQL -- RptSel

```sql
-- ============================================================
-- DQ Rule: A customer must not have payment terms more favorable than the master data standard
-- Rule ID: 0011
-- View: Defects Report (RptSel)
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_0011_{SOURCE_SYSTEM}_KNA1_ZTERM_Customer_Payment_Terms_More_Favorable_Master_RptSel] AS
SELECT
 *

FROM [dbo].[DQ_0011_{SOURCE_SYSTEM}_KNA1_ZTERM_Customer_Payment_Terms_More_Favorable_Master_OptSel]
WHERE [zIsErrorFlag] = 1
;
```

---

## Metadata

- **SKP Rule ID:** SKP_RULE_0006
- **DQOps ID:** 0011
- **Created:** 2026-08-27
- **Owner:** gaurav.kalwani@capgemini.com
- **Version:** 1.0
