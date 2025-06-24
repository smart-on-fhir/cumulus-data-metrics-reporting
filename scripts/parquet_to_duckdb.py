#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "duckdb",
# ]
# ///

import os
import re
import click
import duckdb
import glob


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--db-path", "-d", default="metrics.duckdb", help="Path to the DuckDB database file, defaults to metrics.duckdb")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def load_parquet_files(directory, db_path, verbose):
    """
    Load all .parquet files from DIRECTORY into a DuckDB database.
    
    Table names are derived from filenames, specifically the portion starting with c_ or q_
    and ending at the first period.
    """
    # Connect to DuckDB
    conn = duckdb.connect(db_path)
    
    if verbose:
        click.echo(f"Connected to DuckDB database at: {db_path}")
    
    # Find all parquet files in the directory
    parquet_files = glob.glob(os.path.join(directory, "*.parquet"))
    
    if not parquet_files:
        click.echo(f"No .parquet files found in {directory}")
        return
    
    if verbose:
        click.echo(f"Found {len(parquet_files)} .parquet files")
    
    # Process each parquet file
    for file_path in parquet_files:
        # Extract the base filename
        filename = os.path.basename(file_path)
        
        # Extract table name from filename (from c_ or q_ to the first period)
        match = re.search(r'([cq]_[^.]+)', filename)
        if not match:
            if verbose:
                click.echo(f"Skipping {filename}: Doesn't match naming pattern (c_* or q_*)")
            continue
        
        table_name = match.group(1)
        
        if verbose:
            click.echo(f"Processing {filename} → table '{table_name}'")
        
        try:
            # Create or replace the table from the parquet file
            conn.execute(f"""
                DROP TABLE IF EXISTS {table_name};
                CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}');
            """)
            
            # Get row count for feedback
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            click.echo(f"Created table '{table_name}' with {row_count} rows from {filename}")
            
        except Exception as e:
            click.echo(f"Error processing {filename}: {str(e)}", err=True)
    
    # Print summary of tables in the database
    tables = conn.execute("SHOW TABLES").fetchall()
    click.echo(f"\nDatabase now contains {len(tables)} tables:")
    for i, (table,) in enumerate(tables, 1):
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        click.echo(f"{i}. {table} ({row_count} rows)")
    
    # Close the connection
    conn.close()
    if verbose:
        click.echo("Database connection closed")


if __name__ == "__main__":
    load_parquet_files() 