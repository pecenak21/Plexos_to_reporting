"""
database.py
Features case-insensitive, whitespace-tolerant, and None-safe SQL queries over local Parquet structures.
"""
import os
import re
import duckdb
import pandas as pd

def initialize_database_structures(base_dir):
    try:
        duckdb.query("SELECT 1 FROM mem_fki LIMIT 1")
    except duckdb.CatalogException:
        print("[+] Building high-performance metadata cache...")
        base_dir_clean = str(base_dir).replace('\\', '/')
        
        data_path = f"{base_dir_clean}/data/**/*.parquet"
        fki_path = f"{base_dir_clean}/fullkeyinfo/**/*.parquet"
        period_path = f"{base_dir_clean}/period/**/*.parquet"
        
        duckdb.query(f"CREATE TEMPORARY TABLE mem_fki AS SELECT * FROM read_parquet('{fki_path}')")
        duckdb.query(f"CREATE TEMPORARY TABLE mem_period AS SELECT * FROM read_parquet('{period_path}')")
        duckdb.query(f"CREATE VIEW v_data AS SELECT * FROM read_parquet('{data_path}')")


def get_automatic_scale_factor(base_dir, property_name, target_header, df_units):
    initialize_database_structures(base_dir)
    lookup_prop = property_name[0] if isinstance(property_name, list) else property_name
    
    # Get DB Unit
    query = f"SELECT unitValue FROM mem_fki WHERE LOWER(TRIM(propertyName)) = '{lookup_prop.lower().strip()}' LIMIT 1;"
    row = duckdb.query(query).fetchone()
    db_unit = row[0].strip() if row else ""
    
    # Get Target Unit
    matches = re.findall(r'\(([^)]+)\)', target_header)
    units = [m.strip() for m in matches if not m.strip().isdigit()]
    target_unit = units[-1] if units else ""

    # Lookup in the provided df_units
    match = df_units[
        (df_units['UnitFrom'].str.lower() == db_unit.lower().strip()) & 
        (df_units['UnitTo'].str.lower() == target_unit.lower().strip())
    ]
    
    if not match.empty:
        factor = float(match.iloc[0]['ConversionRate'])
        print(f"    / Unit:  '{db_unit}' > '{target_unit}' | Factor Applied: {factor}")
        return factor, False
    else:
        print(f"    / Unit: No rule for '{db_unit}' > '{target_unit}'")
        return 1.0, True

def pull_pivoted_data(base_dir, property_name, unique_months, category_list=None, class_name=None, emission_gas_name=None, is_rate=False, temporal_pattern="monthly"):
    """
    Executes a high-performance database PIVOT with case-insensitive and trailing-whitespace tolerant filters.
    
    Args:
        base_dir (str): The directory path where the Parquet data files are located.
        property_name (str): The specific metric to query (e.g., 'Electricity Consumption').
        unique_months (list): A list of expected time columns (e.g., ['Jan-2026', 'Feb-2026']) to ensure consistent schema.
        category_list (list/str, optional): A specific category or list of categories to filter by. Defaults to None.
        class_name (str, optional): The class of objects to filter for (e.g., 'Buildings'). Defaults to None.
        emission_gas_name (str, optional): If provided, overrides settings to focus on gas-specific production data. Defaults to None.
        temporal_pattern (str, optional): Defines the aggregation level. Defaults to "monthly"; can be set to "daily".
    """

    # Use the parameter to set the aggregation function
    agg_func = "AVG" if is_rate else "SUM"

    # 1. Prepare environment: Setup local database views on top of Parquet files
    initialize_database_structures(base_dir)
    
    # 2. Build dynamic SQL filter: Create case-insensitive logic for single inputs
    sub_conditions = [f"LOWER(TRIM(f.PropertyName)) = '{property_name.lower().strip()}'"]
    
    # Add class filter if specified
    if class_name and str(class_name).lower().strip() != 'none':
        sub_conditions.append(f"LOWER(TRIM(f.childClassName)) = '{str(class_name).lower().strip()}'")
        
    # Add category filter if specified
    if category_list:
        # Standardize category_list as a list to handle single or multiple values
        cat_items = category_list if isinstance(category_list, list) else [category_list]
        valid_cats = [cat for cat in cat_items if cat is not None and str(cat).lower().strip() != 'all']
        if valid_cats:
            placeholders = ", ".join(f"'{str(cat).lower().strip()}'" for cat in valid_cats)
            sub_conditions.append(f"LOWER(TRIM(f.ChildObjectCategoryName)) IN ({placeholders})")
    
    master_filter = " AND ".join(sub_conditions)
    
    # Override filters if specifically looking for emission gas data
    if emission_gas_name:
        master_filter = f"LOWER(TRIM(f.PropertyName)) = 'generation production'"
        gas_filter = f"AND LOWER(TRIM(f.parentObjectName)) = '{emission_gas_name.lower().strip()}'"
    else:
        gas_filter = ""

    # 3. Configure Temporal Granularity: Set SQL logic for daily vs monthly aggregation
    if temporal_pattern == "daily":
        day_select = "CAST(EXTRACT(DAY FROM CAST(p.StartDate AS TIMESTAMP)) AS INTEGER) AS Day_Id,"
        group_by_clause = "GROUP BY Object_Name, band_id, Year, Day_Id"
    else:
        day_select = ""
        group_by_clause = "GROUP BY Object_Name, band_id, Year"

    # 4. Name Construction: Define object name logic (using child name or parent as fallback)
    obj_name_expr = "(CASE WHEN f.childObjectName IS NULL OR TRIM(f.childObjectName) = '' THEN f.parentObjectName ELSE f.childObjectName END)"

    # 5. Define Pivot Query: Execute SQL to join data, transform dates, and perform pivot
    pivot_query = f"""
        PIVOT (
            SELECT 
                {obj_name_expr} AS Object_Name,
                f.bandId AS band_id,
                CAST(EXTRACT(YEAR FROM CAST(p.StartDate AS TIMESTAMP)) AS INTEGER) AS Year,
                {day_select}
                strftime(CAST(p.StartDate AS TIMESTAMP), '%b-%Y') AS Month_Label,
                d.Value AS Metric_Value
            FROM v_data d
            JOIN mem_fki f ON d.SeriesId = f.seriesId AND d.DataFileId = f.dataFileId
            JOIN mem_period p ON d.PeriodId = p.PeriodId
            WHERE {master_filter}
              {gas_filter}
        )
        ON Month_Label
        USING {agg_func}(Metric_Value)
        {group_by_clause}
    """
    # 6. Execution and Cleanup: Run DuckDB query and sanitize Pandas output
    try:
        df = duckdb.query(pivot_query).df()
        if df.empty: 
            return df

        # Ensure no NULLs in numeric data
        meta_cols = ['Object_Name', 'band_id', 'Year', 'Day_Id']
        pivot_cols = [c for c in df.columns if c not in meta_cols]
        df[pivot_cols] = df[pivot_cols].fillna(0.0)
        
        # Ensure all columns in 'unique_months' exist for consistent downstream reporting
        for m in unique_months:
            if m not in df.columns:
                df[m] = 0.0
                
        return df
    except Exception:
        # Fallback for query execution errors
        return pd.DataFrame()