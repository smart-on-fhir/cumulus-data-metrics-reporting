---
title: Attachments
toc: false
sql:
  metrics: data/metrics.duckdb
---

```js
const formatNumber = d3.format(",");
```

## Diagnostic Report Resources by Attachment Format

```sql id=[{c_content_type_use_diagnosticreport_table}]
  SELECT table_name AS c_content_type_use_diagnosticreport_table
  FROM duckdb_tables() 
  WHERE table_name LIKE '%c_content_type_use_diagnosticreport%'
```

```sql id=[{c_resource_count_diagnosticreport_year_table}]
  SELECT table_name AS c_resource_count_diagnosticreport_year_table
  FROM duckdb_tables() 
  WHERE table_name LIKE '%c_resource_count_diagnosticreport_year%'
```

```js
const resource_count_diagnosticreport = sql([`
	SELECT CASE 
		WHEN content_types = 'cumulus__none'  THEN 'none'
		ELSE content_types
	END AS content_types,
	sum(cnt) AS cnt,
	round(sum(cnt) / (
      SELECT sum(cnt) 
      FROM metrics.${c_resource_count_diagnosticreport_year_table}
    ), 2) AS pct,
	FROM metrics.${c_content_type_use_diagnosticreport_table}
	GROUP BY 1
	HAVING pct > 0
`])
```

```js
Plot.plot({
  marginLeft: 10,
  height: 100,
  y: {
    label: null,
    domain: ["Total"],
    axis: false
  },
  x: {
    label: "Percentage",
    domain: [0, 1],
    tickFormat: d => d * 100 + "%"
  },
  color: {
    legend: true,
    label: "Content Types"
  },
  marks: [
    Plot.barX(resource_count_diagnosticreport, 
      Plot.stackX({
        x: "pct",
        y: () => "Total",
        fill: "content_types",
        title: d => `${d.content_types}: ${formatNumber(d.cnt)} (${(d.pct * 100).toFixed(1)}%)`
      })
    )
  ]
})
```

## Document Reference Resources by Attachment Format

```sql id=[{c_content_type_use_documentreference_table}]
  SELECT table_name AS c_content_type_use_documentreference_table
  FROM duckdb_tables() 
  WHERE table_name LIKE '%c_content_type_use_documentreference%'
```

```sql id=[{c_resource_count_documentreference_year_table}]
  SELECT table_name AS c_resource_count_documentreference_year_table
  FROM duckdb_tables() 
  WHERE table_name LIKE '%c_resource_count_documentreference_year%'
```

```js
const resource_count_documentreference = sql([`
	SELECT CASE 
		WHEN content_types = 'cumulus__none'  THEN 'none'
		ELSE content_types
	END AS content_types,
	sum(cnt) AS cnt,
	round(sum(cnt) / (
      SELECT sum(cnt) 
      FROM metrics.${c_resource_count_documentreference_year_table}
    ), 2) AS pct,
	FROM metrics.${c_content_type_use_documentreference_table}
	GROUP BY 1
	HAVING pct > 0
`])
```

```js
Plot.plot({
  marginLeft: 10,
  height: 100,
  y: {
    label: null,
    domain: ["Total"],
    axis: false
  },
  x: {
    label: "Percentage",
    domain: [0, 1],
    tickFormat: d => d * 100 + "%"
  },
  color: {
    legend: true,
    label: "Content Types"
  },
  marks: [
    Plot.barX(resource_count_documentreference, 
      Plot.stackX({
        x: "pct",
		order: "content_types",
        y: () => "Total",
        fill: "content_types",
        title: d => `${d.content_types}: ${formatNumber(d.cnt)} (${(d.pct * 100).toFixed(1)}%)`
      })
    )
  ]
})
```