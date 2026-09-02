# DQ Rule: BOMs MUST NOT include their own finished assembly as a component.

## Rule Header

### Rule

| Field | Value |
|-------|-------|
| SKP Rule ID | SKP_RULE_0011 |
| Rule Name | BOMs MUST NOT include their own finished assembly as a component. |
| Rule Name Score | 98% |
| Data Domain | Bill of Material |
| Object Type | Master |
| Business Process | Production Planning |
| Business Impact | Critical |
| Rule Type | Error |
| Source | SAP HANA Mock IV |

### Implementation (this view)

| Field | Value |
|-------|-------|
| DQOps ID | 0011 |
| System | SRCECCZ02100 (alias: P02) |
| View Type | OptSel |
| Generated View | `DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_OptSel` |

### Description

1. Functional/Business Description
   Identifying Bill of Material component records where the component item (IDNRK) is not empty and matches the parent BOM header item number (STLNR), creating a recursive structure that can break BOM explosion and distort material requirements.

2. Specific Relevancy Criteria/Scope
   All active Bill of Material component records (STPO) with BOM categories in ('L','I','N','C') that are not flagged for deletion and have valid effectivity dates.

3. DQ Checks (Conditions)
   - Fetch
      - All active BOM component records (STPO) for BOM headers (STKO) with valid material masters (MAST), excluding deletion-flagged records.
   - Check - Mark any record where:
      - BOM Component (IDNRK) is populated AND equals the parent finished assembly (STLNR), creating a recursive BOM structure.
   - Return
      - ALL records that fail the above check.

## Output Fields

### Technical Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 1 | zSourceSystemID | STKO.zSourceSystemID |  |  |  | Yes |
| 2 | zConcatenatedKey |  | Calculated |  | Concatenate: STKO.STLTY + '_' + STKO.STLNR + '_' + STPO.STPOZ | Yes |
| 3 | zIsErrorFlag |  | BIT (1/0) |  | Derived from Logic: 1 = fails DQ check (recursive BOM), 0 = passes DQ check (not recursive) |  |

### Basic Fields

| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 4 | BOM Type | STKO.STLTY |  |  |  | Yes |
| 5 | BOM Number | STKO.STLNR |  |  |  | Yes |
| 6 | BOM Item Number | STPO.STPOZ |  |  |  | Yes |
| 7 | BOM Component | STPO.IDNRK |  |  |  |  |
| 8 | Component Quantity | STPO.MENGE |  |  |  |  |
| 9 | Component Unit of Measure | STPO.MEINS |  |  |  |  |

## Logic / Check Conditions

| Element | Operator | Table.Field | Value | Instruction |
|---------|----------|-------------|-------|-------------|
| BOM Component Matches Parent Assembly | = | STPO.IDNRK = STKO.STLNR | 1 - If (STPO.IDNRK = STKO.STLNR)<br>0 - If (STPO.IDNRK <> STKO.STLNR) | zIsErrorFlag = 1 when component equals parent (recursive)<br>zIsErrorFlag = 0 when component differs from parent |

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---------|--------|--------|------|-----|-------------|
| STPO -> STKO | STPO | STKO | INNER JOIN | MANDT, STLTY, STLNR |  |
| STKO -> MAST | STKO | MAST | INNER JOIN | MANDT, STLNR (STLNR=MATNR) |  |

## Filters

### Inclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Limit to source system P02 (SRCECCZ02100) | = | STKO | zSourceSystemID | 'SRCECCZ02100' |
| Limit to valid BOM categories | IN | STPO | POSTP | ('L','I','N','C') |
| Limit to non-empty BOM components | IS NOT NULL | STPO | IDNRK | NULLIF(TRIM(IDNRK), '') IS NOT NULL |

### Exclusions

| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Exclude BOM headers flagged for deletion | <> | STKO | LOEKZ | IF STKO.LOEKZ = 'X' THEN Exclude |
| Exclude BOM components flagged for deletion | <> | STPO | LKENZ | IF STPO.LKENZ = 'X' THEN Exclude |
| Exclude expired BOM headers | <> | STKO | VALID_TO | IF STKO.VALID_TO < '99991231' THEN Exclude |

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: BOMs MUST NOT include their own finished assembly as a component.
-- Rule ID: 0011
-- View:    Opportunity Report (OptSel) (DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_OptSel)
-- Generated: 2026-09-01T11:28:10
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_OptSel] AS
SELECT

    -- Syniti Technical Fields
    STKO.zSourceSystemID AS [zSourceSystemID],
    CONCAT(STKO.STLTY, '_', STKO.STLNR, '_', STPO.STPOZ) AS [zConcatenatedKey],
    CASE
        WHEN NULLIF(TRIM(STPO.IDNRK), '') IS NOT NULL
        THEN 1
        ELSE 0
    END AS [zIsErrorFlag],

    -- Basic Fields
    STKO.STLTY AS [BOM Type],
    STKO.STLNR AS [BOM Number],
    STPO.STPOZ AS [BOM Item Number],
    STPO.IDNRK AS [BOM Component],
    STPO.MENGE AS [Component Quantity],
    STPO.MEINS AS [Component Unit of Measure]

FROM [WRKDQ].[dbo].[STPO] AS STPO

INNER JOIN [WRKDQ].[dbo].[STKO] AS STKO 
    ON STPO.MANDT = STKO.MANDT 
    AND STPO.STLTY = STKO.STLTY 
    AND STPO.STLNR = STKO.STLNR

INNER JOIN [WRKDQ].[dbo].[MAST] AS MAST 
    ON STKO.MANDT = MAST.MANDT 
    AND STKO.STLNR = MAST.MATNR

WHERE
    /* Exclude: Exclude BOM headers flagged for deletion */
    ISNULL(STKO.LOEKZ, '') <> 'X'
    AND /* Exclude: Exclude BOM components flagged for deletion */
    ISNULL(STPO.LKENZ, '') <> 'X'
    AND /* Exclude: Exclude expired BOM headers */
    ISNULL(STKO.VALID_TO, '99991231') = '99991231'
    AND /* Include: Limit to valid BOM categories */
    NULLIF(TRIM(STPO.POSTP), '') IN ('L','I','N','C')
    AND /* Include: Limit to source system P02 (SRCECCZ02100) */
    STKO.zSourceSystemID = 'SRCECCZ02100'
;
```

## SQL -- RptSel

```sql
-- ============================================================
-- DQ Rule: BOMs MUST NOT include their own finished assembly as a component.
-- Rule ID: 0011
-- View:    Defects Report (RptSel) (DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_RptSel)
-- Generated: 2026-09-01T11:28:10
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_RptSel] AS
SELECT
    *

FROM [dbo].[DQ_0011_P02_STPO_IDNRK_BOM_Component_Not_Empty_OptSel]
WHERE [zIsErrorFlag] = 1
;
```


> Generated: 2026-09-01 · Syniti DQ Studio v4.2.0