---
title: US Core v4 Elements
sql:
  metrics: data/metrics.duckdb
---

```sql id=required_element_tables 
SELECT table_name
FROM duckdb_tables()
WHERE like_escape (table_name, '%c$_us$_core$_v4$_count$_%', '$') 
  AND table_name LIKE '%mandatory%'
ORDER BY table_name
```

```sql id=must_support_tables 
SELECT table_name
FROM duckdb_tables()
WHERE like_escape (table_name, '%c$_us$_core$_v4$_count$_%', '$') 
  AND table_name LIKE '%must%'
ORDER BY table_name
```

```js 
const formatNumber = d3.format(",");

const required_elements = [...required_element_tables].map( t => `
  SELECT 
    '${t.table_name.split("_us_core_v4_count_")
      .slice(-1)[0]
      .replace("_mandatory", "")
      .replace("_must_support", "")
    }' AS resource,
    'mandatory' AS importance,
    *
  FROM metrics.${t.table_name}
`).join("\nUNION BY NAME\n")

const must_support_elements = [...must_support_tables].map( t => `
  SELECT 
    '${t.table_name.split("_us_core_v4_count_")
      .slice(-1)[0]
      .replace("_mandatory", "")
      .replace("_must_support", "")
    }' AS resource,
    'must_support' AS importance,
    *
  FROM metrics.${t.table_name}
`).join("\nUNION BY NAME\n")


const required_elements_by_row = await sql([`
  WITH unpivoted AS (
    UNPIVOT(
      SELECT *
      FROM (${required_elements})
    )
    ON COLUMNS('valid_*')
    INTO NAME element VALUE valid
  ),
  totaled AS (
    SELECT 
      resource, 
      element,
      importance,
      sum(cnt) AS total_cnt
    FROM unpivoted
    GROUP BY 1,2,3
  )
  SELECT
    unpivoted.resource,
    replace(unpivoted.element, 'valid_', '') AS element,
    unpivoted.resource || ' - ' || replace(unpivoted.element, 'valid_', '') 
      AS resource_element,
    CASE 
      WHEN valid = true THEN 'present and valid' 
      ELSE 'missing or invalid' 
    END AS validity,
    unpivoted.importance,
    SUM(cnt) AS cnt,
    round(SUM(cnt) / MAX(total_cnt)*100) AS pct
  FROM unpivoted
  LEFT JOIN totaled 
    ON totaled.element = unpivoted.element
      AND totaled.resource = unpivoted.resource
      AND totaled.importance = unpivoted.importance
  WHERE unpivoted.element != 'valid_mandatory'
  GROUP BY 1,2,3,4,5
  ORDER BY 1,2,3,4,5
`]);

const must_support_elements_by_row = await sql([`
  WITH unpivoted AS (
    UNPIVOT(
      SELECT *
      FROM (${must_support_elements})
    )
    ON COLUMNS('valid_*')
    INTO NAME element VALUE valid
  ),
  totaled AS (
    SELECT 
      resource, 
      element,
      importance,
      sum(cnt) AS total_cnt
    FROM unpivoted
    GROUP BY 1,2,3
  )
  SELECT
    unpivoted.resource,
    replace(unpivoted.element, 'valid_', '') AS element,
    unpivoted.resource || ' - ' || replace(unpivoted.element, 'valid_', '') 
      AS resource_element,
    CASE 
      WHEN valid = true THEN 'present and valid' 
      ELSE 'missing or invalid' 
    END AS validity,
    unpivoted.importance,
    SUM(cnt) AS cnt,
    round(SUM(cnt) / MAX(total_cnt)*100) AS pct
  FROM unpivoted
  LEFT JOIN totaled 
    ON totaled.element = unpivoted.element
      AND totaled.resource = unpivoted.resource
      AND totaled.importance = unpivoted.importance
  WHERE unpivoted.element != 'valid_mandatory'
  GROUP BY 1,2,3,4,5
  ORDER BY 1,2,3,4,5
`]);

const all_elements = [...required_elements_by_row, ...must_support_elements_by_row];
const filtered_elements = view(Inputs.search(all_elements, {placeholder: "filter by resource or element"}));

```

## Mandatory Elements

```js
Plot.plot({
  marginLeft: 300,
  y: {label: null},
  x: {label: "%"},
  color: {
    legend: true, 
    domain: ["present and valid", "missing or invalid"], 
    range: [ "#FFD580", "#f28e2c"] 
  },
  marks: [
    Plot.barX(
      filtered_elements.filter(d => d.importance === "mandatory"), 
      Plot.stackX({
        order: "validity", 
        reverse: true,
        x: "pct",
        y: "resource_element",
        fill: "validity",
        tip: true,
        title: d => `${d.validity}: ${formatNumber(d.cnt)} ${d.pct != null ? "("+Math.round(d.pct)+"%)": "na"}`
      })
    )
  ]
})
```

## Must Support Elements

```js
Plot.plot({
  marginLeft: 300,
  y: {label: null},
  x: {label: "%"},
  color: {
    legend: true, 
    domain: ["present and valid", "missing or invalid"], 
    range: [ "#FFD580", "#f28e2c"] 
  },
  marks: [
    Plot.barX(
      filtered_elements.filter(d => d.importance === "must_support"), 
      Plot.stackX({
        order: "validity", 
        reverse: true,
        x: "pct",
        y: "resource_element",
        fill: "validity",
        tip: true,
        title: d => `${d.validity}: ${formatNumber(d.cnt)} ${d.pct != null ? "("+Math.round(d.pct)+"%)": "na"}`
      })
    )
  ]
})
```

