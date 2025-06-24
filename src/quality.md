---
title: Quality
toc: false
sql:
  metrics: data/metrics.duckdb
---

```sql id=table_names
  SELECT table_name
  FROM duckdb_tables() 
  WHERE like_escape (table_name, '%q$_%$_summary%', '$') 
```

```js
const tables = table_names.toArray().map(t => t.table_name);

const qualityMetrics = [
  {name: "q_ref_target_valid", title: "Reference Targets in Dataset"},
  {name: "q_ref_target_pop", title: "References Populated"},
  {name: "q_date_recent", title: "Dates Are Plausible"},
  {name: "q_valid_us_core_v4", title: "Mandatory US Core Fields Are Populated"},
  {name: "q_system_use", title: "Expected Terminology Systems Are Used"}
].map(m => {
  const table_name = tables.find(t => t.indexOf(m.name) > -1);
  return {...m, table_name}
});

const buildMetricHeading = metricId => {
  const metric = qualityMetrics.find( m => m.name == metricId);
  const slug = metric.title.toLowerCase().replace(" ", "-");

  return html`<h2 id="${slug}" tabindex="-1">
    <a class="observablehq-header-anchor" href="#${slug}">${metric.title}</a>
  </h2>`
}

const getMetricTable = metricId => {
  const metric = qualityMetrics.find( m => m.name == metricId);
  return metric.table_name;
}

const formatNumber = d3.format(",");
```

## Overview

```js

//set globally here, but can move to per metric thresholds if needed
const threshold = 0.05;

const invalidMetricSql = [
  "SELECT metric FROM (",
  qualityMetrics.map( m => [
    `SELECT '${m.name}' AS metric,`, 
    "  sum(numerator) AS numerator,", 
    "  sum(denominator) AS denominator",
    `FROM metrics.${m.table_name}`
  ].join("\n")).join("\nUNION ALL\n"),
  ")",
 "WHERE numerator > 0 AND denominator > 0",
 `AND numerator/denominator >= ${threshold}`
].join("\n")

const [...invalid_metrics] = await sql([invalidMetricSql]);
```

```js
html`<div style="padding-left: 20px;">
  ${qualityMetrics.map( m => html `<div>
    ${invalid_metrics.find(im => im.metric == m.name) ? "❌" : "✅"}&nbsp;
    <a href="#${m.title.toLowerCase().replace(" ", "-")}">${m.title}</a>
  </div>`)}
</div>`
```

```js 
const ref_target_valid = sql([`
  SELECT 
    resource,
    target,
    CASE WHEN denominator > 0 THEN
      round((1-(numerator/denominator))*100, 0)::INT
    ELSE 0
    END AS valid_pct
  FROM  
    metrics.${getMetricTable("q_ref_target_valid")}
  WHERE
    target != 'cumulus__all'
`])
```

```js
Plot.plot({
  padding: 0,
  grid: false,
  x: {
    axis: "top", 
    label: null
  },
  y: {label: null},
  color: {
    type: "linear",
    scheme: "spectral",
    domain: [0, 100]
  },
  marginLeft: 200,
  marks: [
    Plot.cell(ref_target_valid, {
      x: "target", 
      y: "resource", 
      fill: "valid_pct", 
      tip: true,
      inset: 0.5
    }),
    Plot.text(ref_target_valid, {
      x: "target", 
      y: "resource",
      text: (d) => d.valid_pct ? d.valid_pct+"%" : null,
      fill: (d) => d.valid_pct > 70 ? "white" : "black",
      fontWeight: "bold",
      title: "title"
    })
  ]
})
```

${buildMetricHeading("q_ref_target_pop")}

```js 
const ref_target_pop = sql([`
  SELECT 
    resource,
    target,
    CASE WHEN denominator > 0 THEN
      round((1-(numerator/denominator))*100, 0)::INT
    ELSE 0
    END AS valid_pct
    FROM  
    metrics.${getMetricTable("q_ref_target_pop")}
  WHERE
    target != 'cumulus__all'
`])
```


```js
Plot.plot({
  padding: 0,
  grid: false,
  x: {
    axis: "top", 
    label: null
  },
  y: {label: null},
  color: {
    type: "linear",
    scheme: "spectral",
    domain: [0, 100]
  },
  marginLeft: 200,
  marks: [
    Plot.cell(ref_target_pop, {
      x: "target", 
      y: "resource", 
      fill: "valid_pct", 
      inset: 0.5
    }),
    Plot.text(ref_target_pop, {
      x: "target", 
      y: "resource",
      text: (d) => d.valid_pct ? d.valid_pct+"%" : null, 
      fill: (d) => d.valid_pct > 70 ? "white" : "black",
      fontWeight: "bold",
      title: "title"
    })
  ]
})
```

${buildMetricHeading("q_date_recent")}

```js
const date_recent = sql([`
  SELECT
    'invalid' AS validity,
    resource, 
    numerator AS cnt,
    numerator/denominator*100 AS pct, 
  FROM 
    metrics.${getMetricTable("q_date_recent")}
  WHERE 
    subgroup = 'cumulus__all'
  UNION ALL
  SELECT 
    'valid' AS validity, 
    resource, 
    (denominator-numerator) AS cnt,
    ((denominator-numerator)/denominator)*100 AS pct
  FROM 
    metrics.${getMetricTable("q_date_recent")}
  WHERE 
    subgroup = 'cumulus__all'
`])
```

```js
Plot.plot({
  marginLeft: 200,
  y: {label: null},
  x: {label: "%"},
  color: {
    legend: true, 
    domain: ["invalid", "valid"],
    range: ["#f28e2c", "#FFD580"] 
},
  marks: [
    Plot.barX(date_recent, 
      Plot.stackX({
        order: "validity", 
        x: "pct",
        y: "resource",
        fill: "validity",
        tip: true,
        title: d => `${d.validity} resources: ${formatNumber(d.cnt)} ${d.pct != null ? "("+Math.round(d.pct)+"%)": "na"}`
      })
    )
  ]
})
```

${buildMetricHeading("q_valid_us_core_v4")}

```js
const valid_us_core_v4 = sql([`
  SELECT 
    'invalid' AS validity,
    CASE WHEN resource IN ('Observation','DiagnosticReport') THEN
      resource || ' - ' || profile
    ELSE
      resource
    END AS resource_display, 
    numerator AS cnt,
    numerator/denominator*100 AS pct, 
  FROM  
    metrics.${getMetricTable("q_valid_us_core_v4")}
  WHERE 
    (resource NOT IN ('Observation','DiagnosticReport') AND profile IS NOT NULL)
    OR (resource IN ('Observation','DiagnosticReport') AND profile != 'cumulus__all')
  UNION ALL
  SELECT 
    'valid' AS validity, 
    CASE WHEN resource IN ('Observation','DiagnosticReport') THEN
      resource || ' - ' || profile
    ELSE
      resource
    END AS resource_display,
    (denominator-numerator) AS cnt,
    ((denominator-numerator)/denominator)*100 AS pct
  FROM
    metrics.${getMetricTable("q_valid_us_core_v4")}
  WHERE 
    (resource NOT IN ('Observation','DiagnosticReport') AND profile IS NOT NULL)
    OR (resource IN ('Observation','DiagnosticReport') AND profile != 'cumulus__all')
`])
```

```js
Plot.plot({
  marginLeft: 200,
  y: {label: null},
  x: {label: "%"},
  color: {
    legend: true, 
    domain: ["invalid", "valid"], 
    range: ["#f28e2c", "#FFD580"] 
  },
  marks: [
    Plot.barX(valid_us_core_v4, 
      Plot.stackX({
        order: "validity", 
        x: "pct",
        y: "resource_display",
        fill: "validity",
        tip: true,
        title: d => `${d.validity} resources: ${formatNumber(d.cnt)} ${d.pct != null ? "("+Math.round(d.pct)+"%)": "na"}`
      })
    )
  ]
})
```

${buildMetricHeading("q_system_use")}

```js 
const expected_terminologies = sql([`
  SELECT 
    'invalid' AS validity,
    resource || ' - ' || field AS resource_display,
    numerator AS cnt,
    numerator/denominator*100 AS pct, 
  FROM
    metrics.${getMetricTable("q_system_use")}
  WHERE
    field != 'cumulus__all'
  UNION ALL
  SELECT 
    'valid' AS validity, 
    resource || ' - ' || field AS resource_display,
    (denominator-numerator) AS cnt,
    ((denominator-numerator)/denominator)*100 AS pct
  FROM
    metrics.${getMetricTable("q_system_use")}
  WHERE
    field != 'cumulus__all'
`])
```

```js
Plot.plot({
  marginLeft: 200,
  y: {label: null},
  x: {label: "%"},
  color: {
    legend: true, 
    domain: ["invalid", "valid"], 
    range: ["#f28e2c", "#FFD580"] 
  },
  marks: [
    Plot.barX(expected_terminologies, 
      Plot.stackX({
        order: "validity", 
        x: "pct",
        y: "resource_display",
        fill: "validity",
        tip: true,
        title: d => `${d.validity} resources: ${formatNumber(d.cnt)} ${d.pct != null ? "("+Math.round(d.pct)+"%)": "na"}`
      })
    )
  ]
})
```