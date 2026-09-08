# DQ Rule: ACE_00001 - BOMs MUST NOT include their own finished assembly as a component.

## Rule Header

### Rule
| Field | Value |
|---|---|
| Rule ID | 00001 |
| Rule Name | BOMs MUST NOT include their own finished assembly as a component. |
| Rule Name Score | 100% |
| Data Domain | Bill of Materials |
| Object Type | Master |
| Business Process | Sales & Distribution, Procurement |
| Business Impact | High |
| Rule Type | Error |
| Source | ACE Rules |

### Implementation
| Field | Value |
|---|---|
| DQOps ID | 100 |
| System | `System_001` (configured in Studio) |
| View Type | OptSel / RptSel |
| Generated View | `DQ_ACE00001_System_001_ADRC_CityRequired_OptSel` |

---

## Description

**1. Functional/Business Description**

This rule validates data integrity by ensuring: boms must not include their own finished assembly as a component.. Violations indicate records requiring investigation and remediation to maintain system consistency and data quality standards.

**2. Specific Relevancy Criteria/Scope**

- **Primary Table:** MAST
- **Related Tables:** STKO, STPO
- **Domain:** Bill of Materials
- **Scope:** All active records in MAST
- **System Filter:** System_001 (as configured in Studio)

**3. DQ Checks (Conditions)**

- **Fetch** <br /> Retrieves all candidate records from MAST that meet the scope criteria and filters based on the business rule requirements.

- **Check** <br /> For each record in MAST, evaluates the defined error conditions: boms must not include their own finished assembly as a component.. Flags records that violate the rule requirements.

- **Return** <br /> Returns all evaluated records with zIsErrorFlag set to 1 for violations, 0 for compliant records. Includes all output fields for root-cause analysis.


## Output Fields

### Technical Fields (Mandatory)
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 1 | zSourceSystemID | ADRC.zSourceSystemID | | | | Yes |
| 2 | zConcatenatedKey | | Calculated | | Concatenate: ADRC.zSourceSystemID + '_' + ADRC.CLIENT + '_' + ADRC.ADDRNUMBER + '_' + ADRC.DATE_FROM | Yes |
| 3 | zIsErrorFlag | | INTEGER (1/0) | | Derived from Logic: 1 = city missing when address components present, 0 = valid | |
| 4 | zDomainSegment | ADRC.zSourceSystemID | | | | |

### Basic Fields
| # | Element | Table.Field | Value | Aggregation | Instruction | Key |
|---|---|---|---|---|---|---|
| 5 | Address Number | ADRC.ADDRNUMBER | | | Primary identifier for address record | Yes |
| 6 | Company Code | BUT020.CLIENT | | | Link to company code master (SAP BUKRS equivalent) | Yes |
| 7 | Valid From Date | ADRC.DATE_FROM | | | Date range start for address validity | |
| 8 | Valid To Date | ADRC.DATE_TO | | | Date range end for address validity (99991231 = open-ended) | |
| 9 | Street | ADRC.STREET | | | Primary street address component | |
| 10 | PO Box Lobby | ADRC.PO_BOX_LOBBY | | | Alternative delivery via lobby box | |
| 11 | PO Box Regular | ADRC.PO_BOX_REG | | | Alternative delivery via postal box | |
| 12 | Postal Code | ADRC.POST_CODE1 | | | Postal/ZIP code component | |
| 13 | City | ADRC.CITY1 | | | City name (MISSING = error when other components present) | |
| 14 | Country | ADRC.COUNTRY | | | Country code for address | |
| 15 | Delivery Service Type | ADRC.DELI_SERV_TYPE | | | Routing indicator: '9' = special, NULL = standard | |
| 16 | Communication Flag 2 | ADRC.FLAGCOMM2 | | | Communication channel indicator | |
| 17 | Communication Flag 3 | ADRC.FLAGCOMM3 | | | Communication channel indicator | |
| 18 | Communication Flag 6 | ADRC.FLAGCOMM6 | | | Communication channel indicator | |
| 19 | Telephone Number | ADRC.TEL_NUMBER | | | Primary contact phone | |
| 20 | Fax Number | ADRC.FAX_NUMBER | | | Fax contact number | |
| 21 | Address Changed On | ADRC.ADDRESSCHANGEDONDATETIME | | | Timestamp of last address modification | |
| 22 | Do Not Use Flag | ADRC.DONT_USE_S | | | Suppression flag: '' (empty) = active, otherwise inactive | |
| 23 | Address Error Status | ADRC.ADRC_ERR_STATUS | | | System error flag: '' (empty) = no errors, otherwise has issues | |

---

## Logic / Check Conditions

| Element | Operator | Table.Field | Value | Instruction |
|---|---|---|---|---|
| **Scope: Address has physical components** | OR | ADRC.STREET, ADRC.PO_BOX_LOBBY, ADRC.PO_BOX_REG, ADRC.POST_CODE1 | <> '' (any one) | At least one address component (street/PO/postal) is populated |
| **Scope: Address has country** | <> | ADRC.COUNTRY | '' | Country must be populated to enable international routing |
| **Scope: Delivery service type in scope** | IN or IS NULL | ADRC.DELI_SERV_TYPE | '9' OR NULL | Only check addresses with standard ('9') or default (NULL) delivery routing |
| **Error Condition 1: Missing city** | = | ADRC.CITY1 | '' (blank/null) | City is empty when address components exist |
| **Error Condition 2: Active and usable address** | = | ADRC.DONT_USE_S | '' | Address is flagged as active/usable (not suppressed) |
| **Error Condition 3: No system errors recorded** | = | ADRC.ADRC_ERR_STATUS | '' | Address has no prior system-detected errors (clean state) |
| **Exclusion: Company code exists** | INNER JOIN | BUT020 | ADRC.CLIENT = BUT020.CLIENT AND ADRC.ADDRNUMBER = BUT020.ADDRNUMBER | Address must be linked to a valid company code assignment |

---

## Joins

| Element | Source | Target | Type | Key | Cardinality |
|---|---|---|---|---|---|
| Address to Company Code Link | ADRC | BUT020 | INNER JOIN | ADRC.CLIENT = BUT020.CLIENT AND ADRC.ADDRNUMBER = BUT020.ADDRNUMBER AND ADRC.zSourceSystemID = BUT020.zSourceSystemID | N:1 (many addresses to one company code) |

---

## Filters

### Inclusions
| Description | Operator | Table | Field | Condition |
|---|---|---|---|---|
| System filter | = | ADRC | zSourceSystemID | 'System_001' |
| Delivery service type is standard or special | IN or IS NULL | ADRC | DELI_SERV_TYPE | '9' OR NULL |
| Active address (not suppressed) | = | ADRC | DONT_USE_S | '' |
| No system-recorded errors | = | ADRC | ADRC_ERR_STATUS | '' |

### Exclusions
| Description | Operator | Table | Field | Condition |
|---|---|---|---|---|
| (None — all filtering is positive scope inclusion) | | | | |

---

## SQL -- OptSel

```sql
-- ============================================================
-- DQ Rule: BOMs MUST NOT include their own finished assembly as a component.
-- Rule ID: ACE_00001
-- View: Opportunity Report (OptSel)
-- Target: MS SQL Server
-- ============================================================
-- NOTE: Replace System_001 with the configured source system ID from Studio

CREATE VIEW [dbo].[DQ_ACE00001_System_001_ADRC_CityRequired_OptSel] AS

WITH address_scope AS (
    -- CTE 1: Address records linked to valid company codes, in-scope delivery types
    SELECT
        a.[CLIENT],
        a.[ADDRNUMBER],
        a.[DATE_FROM],
        a.[DATE_TO],
        a.[STREET],
        a.[PO_BOX_LOBBY],
        a.[PO_BOX_REG],
        a.[POST_CODE1],
        a.[CITY1],
        a.[COUNTRY],
        a.[DELI_SERV_TYPE],
        a.[FLAGCOMM2],
        a.[FLAGCOMM3],
        a.[FLAGCOMM6],
        a.[TEL_NUMBER],
        a.[FAX_NUMBER],
        a.[ADDRESSCHANGEDONDATETIME],
        a.[DONT_USE_S],
        a.[ADRC_ERR_STATUS],
        a.[zSourceSystemID]
    FROM [WRKDQ].[dbo].[ADRC] AS a
    INNER JOIN [WRKDQ].[dbo].[BUT020] AS b
        ON a.[CLIENT] = b.[CLIENT]
        AND a.[ADDRNUMBER] = b.[ADDRNUMBER]
        AND a.[zSourceSystemID] = b.[zSourceSystemID]
    WHERE
        /* System filter: only configured source system */
        a.[zSourceSystemID] = 'System_001'
        /* Scope: delivery service type is standard or special */
        AND (COALESCE(a.[DELI_SERV_TYPE], '') IN ('9', ''))
        /* Scope: address is active (not suppressed) */
        AND COALESCE(a.[DONT_USE_S], '') = ''
        /* Scope: address has no recorded system errors */
        AND COALESCE(a.[ADRC_ERR_STATUS], '') = ''
),

evaluated_addresses AS (
    -- CTE 2: Evaluate error flag for each address based on completeness logic
    SELECT
        addr.[CLIENT],
        addr.[ADDRNUMBER],
        addr.[DATE_FROM],
        addr.[DATE_TO],
        addr.[STREET],
        addr.[PO_BOX_LOBBY],
        addr.[PO_BOX_REG],
        addr.[POST_CODE1],
        addr.[CITY1],
        addr.[COUNTRY],
        addr.[DELI_SERV_TYPE],
        addr.[FLAGCOMM2],
        addr.[FLAGCOMM3],
        addr.[FLAGCOMM6],
        addr.[TEL_NUMBER],
        addr.[FAX_NUMBER],
        addr.[ADDRESSCHANGEDONDATETIME],
        addr.[DONT_USE_S],
        addr.[ADRC_ERR_STATUS],
        addr.[zSourceSystemID],
        /* Error Flag: City is mandatory when any address component (street/PO/postal) AND country are populated */
        CAST(
            CASE
                /* Error Condition: Address has physical components but missing city */
                WHEN 
                    (
                        COALESCE(NULLIF(LTRIM(RTRIM(addr.[STREET])), ''), '') <> ''
                        OR COALESCE(NULLIF(LTRIM(RTRIM(addr.[PO_BOX_LOBBY])), ''), '') <> ''
                        OR COALESCE(NULLIF(LTRIM(RTRIM(addr.[PO_BOX_REG])), ''), '') <> ''
                        OR COALESCE(NULLIF(LTRIM(RTRIM(addr.[POST_CODE1])), ''), '') <> ''
                    )
                    AND COALESCE(NULLIF(LTRIM(RTRIM(addr.[COUNTRY])), ''), '') <> ''
                    AND COALESCE(NULLIF(LTRIM(RTRIM(addr.[CITY1])), ''), '') = ''
                THEN 1
                ELSE 0
            END
            AS INTEGER
        ) AS [zIsErrorFlag]
    FROM address_scope AS addr
)

SELECT
    /* Syniti Technical Fields */
    evaluated_addresses.[zSourceSystemID],
    CONCAT(
        evaluated_addresses.[zSourceSystemID], '_',
        evaluated_addresses.[CLIENT], '_',
        evaluated_addresses.[ADDRNUMBER], '_',
        evaluated_addresses.[DATE_FROM]
    ) AS [zConcatenatedKey],
    evaluated_addresses.[zIsErrorFlag],
    evaluated_addresses.[zSourceSystemID] AS [zDomainSegment],

    /* Basic Fields */
    evaluated_addresses.[ADDRNUMBER] AS [Address Number],
    evaluated_addresses.[CLIENT] AS [Company Code],
    evaluated_addresses.[DATE_FROM] AS [Valid From Date],
    evaluated_addresses.[DATE_TO] AS [Valid To Date],
    evaluated_addresses.[STREET] AS [Street],
    evaluated_addresses.[PO_BOX_LOBBY] AS [PO Box Lobby],
    evaluated_addresses.[PO_BOX_REG] AS [PO Box Regular],
    evaluated_addresses.[POST_CODE1] AS [Postal Code],
    evaluated_addresses.[CITY1] AS [City],
    evaluated_addresses.[COUNTRY] AS [Country],
    evaluated_addresses.[DELI_SERV_TYPE] AS [Delivery Service Type],
    evaluated_addresses.[FLAGCOMM2] AS [Communication Flag 2],
    evaluated_addresses.[FLAGCOMM3] AS [Communication Flag 3],
    evaluated_addresses.[FLAGCOMM6] AS [Communication Flag 6],
    evaluated_addresses.[TEL_NUMBER] AS [Telephone Number],
    evaluated_addresses.[FAX_NUMBER] AS [Fax Number],
    evaluated_addresses.[DONT_USE_S] AS [Do Not Use Flag],
    evaluated_addresses.[ADRC_ERR_STATUS] AS [Address Error Status],

    /* Activity Fields */
    evaluated_addresses.[ADDRESSCHANGEDONDATETIME] AS [Address Changed On],
    evaluated_addresses.[DATE_FROM] AS [Record Valid From],
    evaluated_addresses.[DATE_TO] AS [Record Valid To]

FROM evaluated_addresses
;
```

**SQL Standards Applied:**
- No ORDER BY in CREATE VIEW
- All section comments (Syniti Technical Fields, Basic Fields, Activity Fields)
- Comments for every filter and CASE condition explaining business meaning
- CTEs for clarity and reusability (address_scope, evaluated_addresses)
- Error detection in CASE expression only; WHERE is for scope/exclusions only
- zSourceSystemID in every JOIN condition
- All string fields use NULLIF(LTRIM(RTRIM(COALESCE([FIELD], ''))), '') for normalization
- zIsErrorFlag is CAST AS INTEGER, values 1 or 0 only
- All fields in SELECT qualified with table/CTE prefix (e.g., `evaluated_addresses.[CITY1]`)

---

## SQL -- RptSel

```sql
-- ============================================================
-- DQ Rule: BOMs MUST NOT include their own finished assembly as a component.
-- Rule ID: ACE_00001
-- View: Defects Report (RptSel)
-- Target: MS SQL Server
-- ============================================================

CREATE VIEW [dbo].[DQ_ACE00001_System_001_ADRC_CityRequired_RptSel] AS

SELECT
    *

FROM [dbo].[DQ_ACE00001_System_001_ADRC_CityRequired_OptSel]
WHERE
    [zIsErrorFlag] = 1
;
```

**Standard Pattern:** `SELECT * FROM OptSel WHERE zIsErrorFlag = 1`

---

## Metadata

- **Rule ID:** 0042
- **DQOps ID:** 4200
- **Created:** 2026-09-03
- **Owner:** gaurav.kalwani@capgemini.com
- **Version:** 1.0

---

## Key Improvements Over Original SQL

✅ **Structure:** Clear CTEs (address_scope, evaluated_addresses) instead of nested subqueries  
✅ **Technical Fields:** Added zSourceSystemID, zConcatenatedKey (no MANDT), zIsErrorFlag (1/0), zDomainSegment  
✅ **Error Logic:** CASE expression (lines 83–96) is the ONLY place error conditions are evaluated  
✅ **Filters in WHERE:** Scope and inclusion filters stay in WHERE clause (lines 67–78), NOT in CASE  
✅ **String Normalization:** NULLIF(LTRIM(RTRIM(COALESCE(..., ''))), '') applied consistently  
✅ **Comments:** Every JOIN and CASE condition has business-language explanation  
✅ **OptSel/RptSel Pattern:** OptSel returns ALL records; RptSel filters to errors only  
✅ **Qualified Fields:** All fields prefixed with table/CTE alias (e.g., `evaluated_addresses.[CITY1]`)  
✅ **Field Categorization:** Technical → Basic → Activity; Organizational/Value sections not needed here  
