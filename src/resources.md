---
title: Resources
sql:
  metrics: data/metrics.duckdb
---

```js
const formatNumber = d3.format(",");
```

```sql id=resource_count_tables 
SELECT table_name 
FROM information_schema.tables
WHERE table_name LIKE '%c_resource_count_%_year' 
    OR table_name LIKE '%c_resource_count_%_all'
ORDER BY table_name
```

```js 
const all_resources = [...resource_count_tables].map( t => `
  SELECT '${t.table_name.split("_").slice(-2)[0]}' AS resource, *
  FROM metrics.${t.table_name}
`).join("\nUNION BY NAME\n")

const [{resource_total_count}] = await sql([`
  SELECT sum(cnt) AS resource_total_count
  FROM (${all_resources})
`])
```

# ${formatNumber(resource_total_count)} Resources
<br/>


```js
const resource_counts = await sql([
  `SELECT 
      CASE
          WHEN category = 'cumulus__all'
            THEN resource || ' (all)'
          WHEN category = 'cumulus__none'
            THEN resource || ' (other)'
          WHEN category IS NOT NULL
            THEN resource || ' (' || category || ')'
          ELSE resource
      END AS resource_display,
      sum(cnt) AS cnt
  FROM (
    SELECT * FROM (${all_resources}) 
    ORDER BY resource, category 
  )
  GROUP BY 1
  ORDER BY 1
  `
])
```

## Count by Category

```js
Plot.plot({
  x: {
    grid: true, 
    label: "count",
    type: "sqrt",
    tickFormat: "s"
  },
  y: {label: null},
  marginLeft: 250,
  marks: [
    Plot.barX(resource_counts, {
        x: "cnt",
        y: "resource_display",
        tip: true,
        fill: "#6cc5b0"
    }),
    Plot.ruleY([0])
  ]
})
```

```js
const resource_counts_by_year = await sql([
    `SELECT 
      CASE
          WHEN category = 'cumulus__all'
            THEN resource || ' (all)'
          WHEN category = 'cumulus__none'
            THEN resource || ' (other)'
          WHEN category IS NOT NULL
            THEN resource || ' (' || category || ')'
          ELSE resource
      END AS resource_display,
        CASE 
          WHEN year = 'cumulus__none' 
            THEN NULL
            ELSE year 
          END::INT AS year,
        sum(cnt) AS cnt
    FROM (
        SELECT * FROM (${all_resources}) 
        ORDER BY resource, category 
    )
    GROUP BY 1,2
    ORDER BY 1,2
    `
])
```

## Resources Generated Per Year

```js
Plot.plot({
  y: {
    grid: true, 
    label: "count",
    type: "sqrt",
    insetTop: 10
  },
  x: {
    tickFormat: d => d.toString()
  },
  axis: null,
  marginLeft: 20,
  marginRight: 20,
  // height: 50 + 100 * d3.groups(resource_counts_by_year, d => d.resource).length,
  marks: [
    Plot.barY(resource_counts_by_year, {
        x: "year",
        y: "cnt",
        fy: "resource_display",
        tip: true,
        title: d => `${d.year || 'no year'}, resources: ${formatNumber(d.cnt)}`,
        fill: "#6cc5b0"
    }),
    Plot.text( resource_counts_by_year, 
      Plot.selectFirst({
        text: "resource_display", 
        fy: "resource_display", 
        frameAnchor: "top-left", 
        dx: 6, 
        dy: 6
      })
    ),
    Plot.frame()
  ]
})
```

## Resources per Patient (Median)


```sql id=[{resources_per_pt_summary_table}]
  SELECT table_name AS resources_per_pt_summary_table
  FROM duckdb_tables() 
  WHERE table_name LIKE '%c_resources_per_pt_summary%'
```

```js 
const resources_per_pt = sql([`
  SELECT 
    resource || CASE 
      WHEN category = 'cumulus__all' THEN ' (all)'
      ELSE ' (' || category || ')'
    END AS resource_display,
    average, 
    median::FLOAT AS median, 
    std_dev, max
  FROM metrics.${resources_per_pt_summary_table}
  WHERE category != 'cumulus__none'
  AND resource != 'cumulus__all'
  ORDER BY resource_display
`]);
```

```js
Plot.plot({
  x: {
    grid: true, 
    label: "median count",
    type: "sqrt",
    tickFormat: "s"
  },
  y: {
    grid: true,
    label: null
  },
  marginLeft: 200,
  marginRight: 100,
  marks: [
    Plot.dot(resources_per_pt, {
      y: "resource_display",
      x: "median",
      title: d => `median: ${formatNumber(d.median)}\naverage: ${formatNumber(d.average)}\nmax: ${formatNumber(d.max)}`,
      stroke:"#6cc5b0", 
      fill: "#6cc5b0",
      tip: true,
      r: 5
    })
  ]
})
```

## Resources per Patient (Max)
```js
Plot.plot({
  x: {
    grid: true, 
    label: "max count",
    type: "sqrt",
    tickFormat: "s"
  },
  y: {
    grid: true,
    label: null
  },
  marginLeft: 200,
  marginRight: 100,
  marks: [
    Plot.dot(resources_per_pt, {
      y: "resource_display",
      x: "max",
      title: d => `median: ${formatNumber(d.median)}\naverage: ${formatNumber(d.average)}\nmax: ${formatNumber(d.max)}`,
      stroke:"#6cc5b0", 
      fill: "#6cc5b0", 
      tip: true,
      r: 5
    })
  ]
})
```