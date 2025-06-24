# Cumulus Data Metrics Reporting

Set of visualizations for [Qualifer](https://github.com/sync-for-science/qualifier/blob/master/metrics.md) FHIR data quality and characterization metrics generated using the open source [Cumulus](https://github.com/smart-on-fhir/cumulus-library-data-metrics) tool. Cumulus can be run directly on files returned from a [Bulk FHIR export]https://hl7.org/fhir/uv/bulkdata/export.html), or on a [Cumulus AWS Athena FHIR data lake](https://docs.smarthealthit.org/cumulus/etl/).

These reports are intended to be a starting point for your FHIR data quality reporting needs, and can be easily customized to highlight different aspects of the Qualifier metrics.

## Demo

Data visualizations of [metrics for a sample patient population](https://docs.smarthealthit.org/cumulus-data-metrics-reporting/) generated with [Synthea](https://github.com/synthetichealth/synthea/wiki).

## Setup

1. Install [git](https://git-scm.com/downloads), [nodejs](https://nodejs.org) and [python](https://www.python.org/)

2. Install the [Cumulus Data Metrics Library](https://github.com/smart-on-fhir/cumulus-library-data-metrics)
    ```
    pip install cumulus-library-data-metrics
    ```

3. Clone this repository
    ```
    git clone {repository path}
    ```

4. Install dependencies
    ```
    npm i
    ```

## Calculate Metrics

1. Follow the instructions outlined in the Cumulus Data Metrics Library [documentation](https://github.com/smart-on-fhir/cumulus-library-data-metrics). 

    When running metrics, be sure to specify a `db-type` of `duckdb`, a `database` named `metrics.duckdb` and set the `output-mode` to `aggregate`. Your command should look something like the one below. Note that you'll need to change the path in the last parameter to point to your actual ndjson data:
    ```
    cumulus-library build \
    --option output-mode:aggregate \
    --option min-bucket-size:0 \
    --db-type duckdb \
    --database src/data/metrics.duckdb \
    --target data_metrics \
    --load-ndjson-dir {path/to/ndjson/root}
    ```

    Alternatively, metrics can be run on AWS Athena instance of [Cumulus](https://docs.smarthealthit.org/cumulus/library/first-time-setup.html) and metric tables can be exported to Parquet and imported into a new DuckDB database at `src/data/metrics.duckdb` using `scripts/parquet_to_duckdb.py` for local visualization.

2. Once the metrics have run, launch the reporting server
    ```
    npm run dev
    ```

3. You can also build a static copy of the report which will generate html files in the `dist` directory that can be loaded onto any web server
    ```
    npm run build
    ```

## Updating and Customizing Reports

The metrics report is built with the open source [Observable Framework](https://observablehq.com/framework/getting-started) and has no other nodejs dependencies.