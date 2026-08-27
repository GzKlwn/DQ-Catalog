# Customer Deletion Rule

## Specification

**Rule Name:** Customer Deletion  
**Object:** Customer  
**Tables:** KNA1 (Customer Master), KNVV (Customer Sales Data)  
**Criticality:** High  
**Industry:** Manufacturing  

### Description

Validates that deleted customer records are properly flagged and do not appear in active transactions.

### Logic

Check for customer records marked as deleted (LVORM = 'X') but still referenced in active orders or invoices.

---

## Fetch

Retrieve all customer records from KNA1 and their associated sales records from KNVV.

---

## Check

Identify customers where:
- Deletion flag is set (LVORM = 'X')
- But still have active documents (VBAK.VBELN) or open items (BSID/BSAD)

---

## Return

Flag: `zIsErrorFlag = 1` if the above condition is met, else `0`

---

## OptSel (Optimized Select)

```sql
SELECT 
    [zConcatenatedKey] = CONCAT(k.KUNNR, '-', v.VBELN),
    [zIsErrorFlag] = CASE 
        WHEN k.LVORM = 'X' AND v.VBELN IS NOT NULL THEN 1 
        ELSE 0 
    END,
    k.KUNNR,
    k.LVORM,
    v.VBELN
FROM KNA1 k
LEFT JOIN KNVV v ON k.KUNNR = v.KUNNR
WHERE k.LVORM = 'X'
```

---

## RptSel (Report Select)

```sql
SELECT * 
FROM [OptSel]
WHERE [zIsErrorFlag] = 1
```

---

## Metadata

- **Created:** 2026-08-27
- **Owner:** gaurav.kalwani@capgemini.com
- **Version:** 1.0
