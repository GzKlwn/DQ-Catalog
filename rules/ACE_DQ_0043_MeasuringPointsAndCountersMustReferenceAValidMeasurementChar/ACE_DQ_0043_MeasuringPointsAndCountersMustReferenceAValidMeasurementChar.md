# DQ Rule: ACE_00043 - Measuring points and counters MUST reference a valid measurement characteristic.

## Rule Header

### Rule
| Field | Value |
|-------|-------|
| Rule ID | 00043 |
| Rule Name | Measuring points and counters MUST reference a valid measurement characteristic. |
| Rule Name Score | 100% |
| Data Domain | Characteristics |
| Object Type | Master |
| Business Process | Data Quality |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|-------|-------|
| DQOps ID | 4300 |
| System | System_001 |
| View Type | OptSel / RptSel |
| Generated View | DQ_0051_System_001_QALS_OptSel |

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: measuring points and counters must reference a valid measurement characteristic.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** CABN
- **Related Tables:** N/A
- **Domain:** Characteristics
- **Scope:** All active records in CABN
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from CABN that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in CABN, evaluates the defined error conditions: measuring points and counters must reference a valid measurement characteristic.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 1 | zSourceSystemID | base.[zSourceSystemID] | | | System identifier | Yes |
| 2 | zConcatenatedKey | | Calculated | | CONCAT: base.[zSourceSystemID] + '_MATNR' + ... | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived: 1=error, 0=valid | |
| 4 | zDomainSegment | base.[zSourceSystemID] | | | Set equal to zSourceSystemID | |

### Basic Fields
| # | Element | Table.Field | Aggregation | Instruction |
|---|---------|-------------|-------------|-------------|
| 1 | MATNR | base.[MATNR] | | Primary key component |
| 2 | Secondary | base.[KEY2] | | Key component |

### Organizational Fields
| # | Element | Table.Field | Aggregation | Instruction |
|---|---------|-------------|-------------|-------------|
| 1 | System | base.[zSourceSystemID] | | Organizational scope |

### Value Fields
| # | Element | Table.Field | Aggregation | Instruction |
|---|---------|-------------|-------------|-------------|
| 1 | N/A | | | No monetary/quantitative fields |

### Activity Fields
| # | Element | Table.Field | Aggregation | Instruction |
|---|---------|-------------|-------------|-------------|
| 1 | Created Date | base.[ERDAT] | | Record creation date |
| 2 | Changed Date | base.[AEDAT] | | Last modification date |

## Logic / Check Conditions

| Element | Operator | Table.Field | Value | Instruction |
|---------|----------|-------------|-------|-------------|
| Primary Condition | = or <> | QALS | Various | Data quality validation per rule |

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---------|--------|--------|------|-----|-------------|
| System Filter | QALS | All | Alignment | zSourceSystemID = 'System_001' | N/A |

## Filters

### Inclusions
| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| System Filter | = | QALS | zSourceSystemID | System_001 |

### Exclusions
| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Exclude Deleted | <> | QALS | LVORM | X |

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: Measuring points and counters MUST reference a valid measurement characteristic.
-- Rule ID: ACE_00043
-- View: Opportunity Report (OptSel)
-- Target: MS SQL Server
-- ============================================================
-- NOTE: Replace System_001 with the configured source system ID from Studio

CREATE VIEW [dbo].[DQ_ACE00043_System_001_QALS_OptSel] AS

WITH evaluated_items AS (
    -- CTE: Evaluate all candidate records for error conditions
    SELECT
        /* Syniti Technical Fields */
        base.[zSourceSystemID],
        CAST(CONCAT(
            base.[zSourceSystemID],
            '_',
            MATNR
        ) AS NVARCHAR(MAX)) AS [zConcatenatedKey],
        base.[zSourceSystemID] AS [zDomainSegment],

        /* Basic Fields */
                base.[MATNR],

        /* Error Flag: Derived from business rule logic */
        CAST(
            CASE
                WHEN 1 = 1 THEN 0  -- Replace with actual error detection logic
                ELSE 0
            END
            AS INTEGER
        ) AS [zIsErrorFlag],

        /* Activity Fields */
        base.[ERDAT] AS [Created Date],
        base.[AEDAT] AS [Changed Date]

    FROM [WRKDQ].[dbo].[QALS] AS base
    WHERE
        /* System filter: Organizational scope */
        base.[zSourceSystemID] = 'System_001'
        /* Exclude deleted records */
        AND COALESCE(base.[LVORM], '') <> 'X'
)

SELECT
    /* Syniti Technical Fields */
    evaluated_items.[zSourceSystemID],
    evaluated_items.[zConcatenatedKey],
    evaluated_items.[zIsErrorFlag],
    evaluated_items.[zDomainSegment],

    /* Basic Fields */
        evaluated_items.[MATNR],

    /* Organizational Fields */
    evaluated_items.[zSourceSystemID] AS [System],

    /* Activity Fields */
    evaluated_items.[Created Date],
    evaluated_items.[Changed Date]

FROM evaluated_items
;
```

## SQL -- RptSel

```sql
-- ============================================================
-- DQ Rule: Measuring points and counters MUST reference a valid measurement characteristic.
-- Rule ID: ACE_00043
-- View: Defects Report (RptSel)
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_ACE00043_System_001_QALS_RptSel] AS

SELECT
    *

FROM [dbo].[DQ_ACE00043_System_001_QALS_OptSel]
WHERE
    /* Error Flag: Return only records flagged as violations */
    [zIsErrorFlag] = 1
;
```

## Metadata

| Field | Value |
|-------|-------|
| Rule ID | 00043 |
| DQOps ID | 4300 |
| Created | 2026-09-04 |
| Owner | Data Quality Team |
| Version | 1.0 |
| Status | Active |
| System | MS SQL Server |
| Compliance | Syniti Methodology 2024 |
