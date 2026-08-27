# DQ Rule: An invoice must not be issued to a customer with a credit block

## Rule Header

### Rule

| Field | Value |
|-------|-------|
| SKP Rule ID | SKP_RULE_0007 |
| Rule Name | An invoice must not be issued to a customer with a credit block |
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
| DQOps ID | 0013 |
| System | `{SOURCE_SYSTEM}` (configured in Studio) |
| View Type |  |
| Generated View | `DQ_0013_{SOURCE_SYSTEM}_KNA1_FAKSD_Invoice_Issued_Customer_Credit_Block_OptSel` |

### Description

**1. Functional/Business Description**

Issuing invoices to credit-blocked customers creates financial exposure and collection risk. It bypasses credit control processes, potentially increasing bad debt and violating internal credit policies.

**2. Specific Relevancy Criteria/Scope**

Billing documents (VBRK/VBRP) linked to customers with active credit blocks in KNA1 or KNVV.

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieve billing documents from VBRK/VBRP joined to customer master KNA1 and sales area data KNVV via customer number.

- **Check** <br /> Mark any record where: <br /> Invoice exists (VBRK.VBELN is not blank) <br /> AND customer has central billing block (KNA1.FAKSD is not blank) OR sales-area billing block (KNVV.FAKSD is not blank)

- **Return** <br /> Invoices issued to customers with active credit blocks, indicating bypassed credit controls requiring immediate review.

## Output Fields

### Technical Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 1 | zSourceSystemID | KNA1.zSourceSystemID |  |  |  | Yes |
| 2 | zConcatenatedKey |  | Calculated |  | Concatenate: KNA1.zSourceSystemID + '_' + KNA1.KUNNR + '_' + VBRK.VBELN | Yes |
| 3 | zIsErrorFlag |  | BIT (1/0) |  | Derived from Logic: 1 = fails DQ check (candidate), 0 = passes DQ check (compliant) |  |
| 5 | zDomainSegment | KNA1.zDomainSegment |  |  |  |  |

### Basic Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 4 | Customer Number | KNA1.KUNNR |  |  |  | Yes |
| 6 | Customer Name | KNA1.NAME1 |  |  |  |  |
| 7 | Invoice Number | VBRK.VBELN |  |  |  |  |
| 8 | Invoice Type | VBRK.FKART |  |  |  |  |
| 9 | Central Billing Block | KNA1.FAKSD |  |  |  |  |

### Organizational Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 10 | Sales Organization | VBRK.VKORG |  |  |  |  |
| 11 | Company Code | VBRK.BUKRS |  |  |  |  |

### Value Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 12 | Invoice Net Value | VBRK.NETWR |  |  |  |  |
| 13 | Invoice Currency | VBRK.WAERK |  |  |  |  |

### Activity Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 14 | Invoice Date | VBRK.FKDAT |  |  |  |  |

## Logic / Check Conditions

| Element | Operator | Table.Field | Value | Instruction |
|---------|----------|-------------|-------|-------------|
| Central Billing Block populated indicates customer is blocked for billing | <> '' | KNA1.FAKSD |  |  |

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---------|--------|--------|------|-----|-------------|
| VBRK → KNA1 (Customer Master) | VBRK | KNA1 | INNER | VBRK.zSourceSystemID = KNA1.zSourceSystemID AND VBRK.KUNAG = KNA1.KUNNR |  |

## Filters

### Inclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Limit to configured source system | = | KNA1 | zSourceSystemID | `{SOURCE_SYSTEM_ID}` (configured in Studio) |

### Exclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Exclude records flagged for deletion at KNA1 level | <> | KNA1 | LOEVM | 'X' |

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: An invoice must not be issued to a customer with a credit block
-- Rule ID: 0013
-- View: Opportunity Report (OptSel)
-- Target: MS SQL Server
-- ============================================================
-- NOTE: Replace {SOURCE_SYSTEM_ID} with the configured source system ID from Studio

CREATE VIEW [dbo].[DQ_0013_{SOURCE_SYSTEM}_KNA1_FAKSD_Invoice_Issued_Customer_Credit_Block_OptSel] AS
SELECT

 -- Syniti Technical Fields
 KNA1.zSourceSystemID AS [zSourceSystemID],
 /* Key includes invoice number to ensure uniqueness at invoice level */
 CONCAT(KNA1.zSourceSystemID, '_', KNA1.KUNNR, '_', VBRK.VBELN) AS [zConcatenatedKey],
 /* Error when invoice exists for a customer with central billing block */
 CASE
 WHEN ISNULL(KNA1.FAKSD, '') <> '' THEN 1
 ELSE 0
 END AS [zIsErrorFlag],
 KNA1.zDomainSegment AS [zDomainSegment],

 -- Basic Fields
 KNA1.KUNNR AS [Customer Number],
 KNA1.NAME1 AS [Customer Name],
 VBRK.VBELN AS [Invoice Number],
 VBRK.FKART AS [Invoice Type],
 KNA1.FAKSD AS [Central Billing Block],

 -- Organizational Context
 VBRK.VKORG AS [Sales Organization],
 VBRK.BUKRS AS [Company Code],

 -- Value Context
 VBRK.NETWR AS [Invoice Net Value],
 VBRK.WAERK AS [Invoice Currency],

 -- Activity Context
 VBRK.FKDAT AS [Invoice Date]

FROM [WRKDQ].[dbo].[KNA1] AS KNA1

 /* Join to billing documents to identify invoices issued to this customer */
 INNER JOIN [WRKDQ].[dbo].[VBRK] AS VBRK
 ON VBRK.zSourceSystemID = KNA1.zSourceSystemID
 AND VBRK.KUNAG = KNA1.KUNNR /* KUNAG = Sold-to party on billing doc */

WHERE
 /* Exclude records flagged for deletion at customer level */
 ISNULL(KNA1.LOEVM, '') <> 'X'
 /* Limit to configured source system (replace {SOURCE_SYSTEM_ID} with Studio configuration) */
 AND KNA1.zSourceSystemID = '{SOURCE_SYSTEM_ID}'
 /* Only include customers that have a billing block - these are the violations */
 AND ISNULL(KNA1.FAKSD, '') <> ''
;
```

## SQL -- RptSel

```sql
-- ============================================================
-- DQ Rule: An invoice must not be issued to a customer with a credit block
-- Rule ID: 0013
-- View: Defects Report (RptSel)
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_0013_{SOURCE_SYSTEM}_KNA1_FAKSD_Invoice_Issued_Customer_Credit_Block_RptSel] AS
SELECT
 *
FROM [dbo].[DQ_0013_{SOURCE_SYSTEM}_KNA1_FAKSD_Invoice_Issued_Customer_Credit_Block_OptSel]
WHERE [zIsErrorFlag] = 1
;
```

---

## Metadata

- **SKP Rule ID:** SKP_RULE_0007
- **DQOps ID:** 0013
- **Created:** 2026-08-27
- **Owner:** gaurav.kalwani@capgemini.com
- **Version:** 1.0
