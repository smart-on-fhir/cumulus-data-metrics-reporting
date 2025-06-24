---
title: Patients
sql:
  metrics: data/metrics.duckdb
---

<!-- flexible table naming -->

```sql id=[{c_resource_count_patient_all_table}]
  SELECT table_name AS c_resource_count_patient_all_table
  FROM duckdb_tables() 
  WHERE like_escape (table_name, '%c$_resource$_count$_patient$_all%', '$') 
```

```sql id=[{c_pt_count_table}]
  SELECT table_name AS c_pt_count_table
  FROM duckdb_tables() 
  WHERE like_escape (table_name, '%c$_pt$_count%', '$')
```

```sql id=[{c_pt_deceased_count_table}]
  SELECT table_name AS c_pt_deceased_count_table
  FROM duckdb_tables() 
  WHERE like_escape (table_name, '%c$_pt$_deceased$_count%', '$')
```

```js
const formatNumber = d3.format(",");
```

```js
  const [{patient_count}] = await sql([`
    SELECT cnt AS patient_count
    FROM metrics.${c_resource_count_patient_all_table}
  `])
```

#  ${formatNumber(patient_count)} Patients
<br/>

## Birth Decade

```js
const birth_decade = await sql([`
  SELECT
    CASE WHEN birth_year != 'cumulus__none' THEN
      birth_year::INT
    ELSE
      null
    END AS birth_year,
    CASE WHEN deceased THEN 'deceased' ELSE 'alive' END AS pt_state,
    sum(cnt) AS cnt
  FROM 
    metrics.${c_pt_count_table}
  GROUP BY 1,2
`])
const [{no_birth_date}] = await sql([`
  SELECT sum(cnt) AS no_birth_date
  FROM 
    metrics.${c_pt_count_table}
  WHERE 
    birth_year = 'cumulus__none'
`])
```

```js
Plot.plot({
  x: {
    tickFormat: d => d.toString(),
    label: "birth year",
  },
  y: {
    label: "count", 
    grid: true,
  },
  color: {
    legend: true,
    domain: ["alive", "deceased"], range: ["#f28e2c", "#FFD580"] 
  },
  marks: [
    Plot.rectY(
      birth_decade,
      Plot.binX({
        y: "sum",
        title: data => [
          d3.max(data, d=>d.pt_state), "\n",
          d3.min(data, d=>d.birth_year), " - ", 
          d3.max(data, d=>d.birth_year), ": ",
          d3.sum(data, d=>d.cnt)
        ].join("")
      },{
        x: "birth_year",
        y: "cnt",
        fill: "pt_state",
        tip: true,
        interval: 10
      })
    )
  ]
})
```

<small>Date not available: ${formatNumber(no_birth_date)}</small>

## Administrative Gender
```js
const gender = sql([`
  SELECT 
    administrative_gender AS admin_gender, 
    round(sum(cnt) / (
      SELECT 
        sum(cnt) 
      FROM 
        metrics.${c_pt_count_table}
    ), 2) AS pct_cnt,
    sum(cnt) AS cnt
  FROM metrics.${c_pt_count_table}
  GROUP BY 1
`])
```

```js
Plot.plot({
  x: {
    label: "%", 
    percent:true
  },
  color: {
    legend: true,
    scheme: "accent"
  },
  marks: [
    Plot.ruleX([0, 1]),
    Plot.barX(gender, 
      Plot.stackX({
        x: "pct_cnt", 
        fill: "admin_gender",
        fontWeight: "bold",
        insetLeft: 1,
        insetRight: 1,
        channels: {"count": "cnt"},
        tip: true
      })
    ),
    Plot.textX(gender, 
      Plot.stackX({
        x: "pct_cnt", 
        text: d => d.pct_cnt > .25 ? d.admin_gender : null,
        insetLeft: 1,
        insetRight: 1
      })
    )
  ]
})
```

## Deceased Status

```js
const deceased = sql([`
  SELECT
    CASE 
      WHEN deceased THEN 'deceased' 
      ELSE 'alive' 
    END AS pt_state,
    round(sum(cnt) / (
      SELECT sum(cnt) 
      FROM metrics.${c_pt_count_table}
    ), 2) AS pct_cnt,
    sum(cnt) AS cnt
  FROM 
    metrics.${c_pt_count_table}
  GROUP BY 1
`])
```

```js
Plot.plot({
  x: {
    label: "%", 
    percent:true
  },
  color: {
    legend: true,
    scheme: "accent"
  },
  marks: [
    Plot.ruleX([0, 1]),
    Plot.barX(deceased, 
      Plot.stackX({
        order: "deceased", 
        x: "pct_cnt", 
        fill: "pt_state",
        insetLeft: 1,
        insetRight: 1,
        channels: {"count": "cnt"},
        tip: true
      })
    ),
    Plot.textX(deceased, 
      Plot.stackX({
        order: "pt_state", 
        x: "pct_cnt", 
        text: d => d.pct_cnt > .25 ? d.pt_state : null, 
        fontWeight: "bold",
        insetLeft: 1,
        insetRight: 1
      })
    )
  ]
})
```

## Race and Ethnicity
```js 
const race_ethnicity = sql([`
  SELECT 
    ethnicity, 
    race, 
    sum(cnt) AS cnt
  FROM 
    metrics.${c_pt_count_table}
  GROUP BY 1,2
`])
```

```js
Plot.plot({
  x: {axis: null},
  y: {
    tickFormat: "s", 
    grid: true, 
    label: "count"
  },
  color: {legend: true},
  marks: [
    Plot.barY(race_ethnicity, {
      x: "race",
      y: "cnt",
      fill: "race",
      fx: "ethnicity",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

## Age at Death

```js
const age_at_death = sql([`
  SELECT age::INT AS age, sum(cnt) AS cnt
  FROM metrics.${c_pt_deceased_count_table}
  GROUP BY 1
`])
```

```js
Plot.plot({
  x: {
    label: "count", 
    grid: true,
    interval: 1
  },
  marks: [
    Plot.barX(age_at_death, {
      y: "age",
      x: "cnt",
      fill: "#f28e2c"
    })
  ]
})
```