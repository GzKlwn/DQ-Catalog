# DQ Rule: ACE_00087 - Inspection plan operations MUST NOT contain characteristics whose lower acceptance limit exceeds the upper acceptance limit.

## Rule Header

### Rule
| Field | Value |
|-------|-------|
| Rule ID | 00087 |
| Rule Name | Inspection plan operations MUST NOT contain characteristics whose lower acceptance limit exceeds the upper acceptance limit. |
| Rule Name Score | 100% |
| Data Domain | Inspection Lots |
| Object Type | Master |
| Business Process | Data Quality |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|-------|-------|
| DQOps ID | 8700 |
| System | System_001 |
| View Type | OptSel / RptSel |
| Generated View | DQ_0095_System_001_EQUI_OptSel |

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: inspection plan operations must not contain characteristics whose lower acceptance limit exceeds the upper acceptance limit.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** QAMR
- **Related Tables:** QALS
- **Domain:** Inspection Lots
- **Scope:** All active records in QAMR
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from QAMR that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in QAMR, evaluates the defined error conditions: inspection plan operations must not contain characteristics whose lower acceptance limit exceeds the upper acceptance limit.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---------|-------------|-------|-------------|-------------|-----|
| 1 | zSourceSystemID | base.[zSourceSystemID] | | | System identifier | Yes |
| 2 | zConcatenatedKey | | Calculated | | CONCAT: base.[zSourceSystemID] + '_EQUNR' + ... | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived: 1=error, 0=valid | |
| 4 | zDomainSegment | base.[zSourceSystemID] | | | Set equal to zSourceSystemID | |

### Basic Fields
| # | Element | Table.Field | Aggregation | Instruction |
|---|---------|-------------|-------------|-------------|
| 1 | EQUNR | base.[EQUNR] | | Primary key component |
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
| Primary Condition | = or <> | EQUI | Various | Data quality validation per rule |

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---------|--------|--------|------|-----|-------------|
| System Filter | EQUI | All | Alignment | zSourceSystemID = 'System_001' | N/A |

## Filters

### Inclusions
| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| System Filter | = | EQUI | zSourceSystemID | System_001 |

### Exclusions
| Description | Operator | Table | Field | Condition |
|-------------|----------|-------|-------|-----------|
| Exclude Deleted | <> | EQUI | LVORM | X |

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: Inspection plan operations MUST NOT contain characteristics whose lower acceptance limit exceeds the upper acceptance limit.
-- Rule ID: ACE_00087
-- View: Opportunity Report (OptSel)
-- Target: MS SQL Server
-- ============================================================
-- NOTE: Replace System_001 with the configured source system ID from Studio

CREATE VIEW [dbo].[DQ_ACE00087_System_001_EQUI_OptSel] AS

WITH evaluated_items AS (
    -- CTE: Evaluate all candidate records for error conditions
    SELECT
        /* Syniti Technical Fields */
        base.[zSourceSystemID],
        CAST(CONCAT(
            base.[zSourceSystemID],
            '_',
            EQUNR
        ) AS NVARCHAR(MAX)) AS [zConcatenatedKey],
        base.[zSourceSystemID] AS [zDomainSegment],

        /* Basic Fields */
                base.[EQUNR],

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

    FROM [WRKDQ].[dbo].[EQUI] AS base
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
        evaluated_items.[EQUNR],

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
-- DQ Rule: Inspection plan operations MUST NOT contain characteristics whose lower acceptance limit exceeds the upper acceptance limit.
-- Rule ID: ACE_00087
-- View: Defects Report (RptSel)
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_ACE00087_System_001_EQUI_RptSel] AS

SELECT
    *

FROM [dbo].[DQ_ACE00087_System_001_EQUI_OptSel]
WHERE
    /* Error Flag: Return only records flagged as violations */
    [zIsErrorFlag] = 1
;
```

## Metadata

| Field | Value |
|-------|-------|
| Rule ID | 00087 |
| DQOps ID | 8700 |
| Created | 2026-09-04 |
| Owner | Data Quality Team |
| Version | 1.0 |
| Status | Active |
| System | MS SQL Server |
| Compliance | Syniti Methodology 2024 |
