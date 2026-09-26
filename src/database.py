"""
database.py
Features case-insensitive, whitespace-tolerant, and None-safe SQL queries over local Parquet structures.
"""
import os
import re
import functools
import duckdb
import pandas as pd

import exceptions_report

# Set once the temp tables/view exist for the current DuckDB session, so repeated
# calls skip the "does mem_fki already exist" round-trip (initialize_database_structures
# is invoked on every pull_pivoted_data / get_automatic_scale_factor call).
_db_initialized = False

def initialize_database_structures(base_dir):
    global _db_initialized
    if _db_initialized:
        return
    try:
        duckdb.query("SELECT 1 FROM mem_fki LIMIT 1")
        _db_initialized = True
    except duckdb.CatalogException:
        print("[+] Building high-performance metadata cache...")
        base_dir_clean = str(base_dir).replace('\\', '/')

        data_path = f"{base_dir_clean}/data/**/*.parquet"
        fki_path = f"{base_dir_clean}/fullkeyinfo/**/*.parquet"
        period_path = f"{base_dir_clean}/period/**/*.parquet"

        duckdb.query(f"CREATE TEMPORARY TABLE mem_fki AS SELECT * FROM read_parquet('{fki_path}')")
        duckdb.query(f"CREATE TEMPORARY TABLE mem_period AS SELECT * FROM read_parquet('{period_path}')")
        duckdb.query(f"CREATE VIEW v_data AS SELECT * FROM read_parquet('{data_path}')")
        _db_initialized = True


def _key_filter(property_name, class_name=None, parent_name=None):
    """mem_fki conditions (alias f) selecting one property's series, optionally narrowed by class and parent object."""
    conditions = [f"LOWER(TRIM(f.PropertyName)) = '{str(property_name).lower().strip()}'"]
    if class_name and str(class_name).lower().strip() != 'none':
        conditions.append(f"LOWER(TRIM(f.ChildClassName)) = '{str(class_name).lower().strip()}'")
    if parent_name:
        conditions.append(f"LOWER(TRIM(f.ParentObjectName)) = '{str(parent_name).lower().strip()}'")
    return " AND ".join(conditions)


@functools.lru_cache(maxsize=None)
def resolve_period_type(property_name, class_name=None, parent_name=None, temporal_pattern="monthly", is_rate=False):
    """
    The one Plexos period type a query reads from.

    A solution stores each property at several resolutions (Interval, Day, Month, Year),
    each a separate series in mem_fki. Mixing them in one pull adds the monthly and annual
    totals on top of the summed intervals, so every query reads exactly one.

    Summed properties read Plexos's own Day (daily patterns) or Month totals. Rate
    properties are averaged from Interval values instead: Plexos's summary value for a
    rate is not always that average -- a renewable's monthly Capacity Factor is 100%
    against its available capacity, where the hourly average is ~40%.
    """
    summary = "day" if temporal_pattern in ("daily", "daily-summary") else "month"
    order = ["interval", summary] if is_rate else [summary, "interval"]
    available = {r[0] for r in duckdb.query(
        f"SELECT DISTINCT LOWER(TRIM(f.PeriodTypeName)) FROM mem_fki f WHERE {_key_filter(property_name, class_name, parent_name)}"
    ).fetchall()}
    for period_type in order:
        if period_type in available:
            if period_type != order[0]:
                exceptions_report.record_period_fallback(property_name, class_name, order[0], period_type)
            return period_type
    return order[0]


@functools.lru_cache(maxsize=None)
def _lookup_db_unit(base_dir, lookup_prop, class_name=None, parent_name=None, period_type="month"):
    # mem_fki is static for the lifetime of a report run, so the same key always resolves
    # to the same unit -- and this gets called once per property per parent object in
    # nested blocks. The unit differs by period type (MW per interval, GWh per month) and
    # by class/membership (Offtake is BBtu for a generator, 1000·MMBTU for the system),
    # so it is looked up on the same key the data is pulled with.
    query = f"""SELECT DISTINCT TRIM(f.UnitValue) FROM mem_fki f
                WHERE {_key_filter(lookup_prop, class_name, parent_name)}
                  AND LOWER(TRIM(f.PeriodTypeName)) = '{period_type}'
                ORDER BY 1"""
    units = [r[0] for r in duckdb.query(query).fetchall() if r[0]]
    if len(units) > 1:
        exceptions_report.record_mixed_units(lookup_prop, class_name, units)
    return units[0] if units else ""


def get_db_unit(base_dir, property_name, class_name=None, parent_name=None, temporal_pattern="monthly", is_rate=False):
    """Unit of the series pull_pivoted_data reads for the same arguments."""
    initialize_database_structures(base_dir)
    period_type = resolve_period_type(property_name, class_name, parent_name, temporal_pattern, bool(is_rate))
    return _lookup_db_unit(base_dir, property_name, class_name, parent_name, period_type)


def get_automatic_scale_factor(base_dir, property_name, df_units, explicit_unit, class_name=None, parent_name=None, temporal_pattern="monthly", is_rate=False):
    lookup_prop = property_name[0] if isinstance(property_name, list) else property_name

    # Get DB Unit, for the same series the data was pulled from
    db_unit = get_db_unit(base_dir, lookup_prop, class_name, parent_name, temporal_pattern, is_rate)

    # Target Unit is now strictly the explicit unit passed from the blueprint
    target_unit = str(explicit_unit).strip() if explicit_unit and str(explicit_unit).strip().lower() != 'nan' else ""
    if not target_unit:
        # A blank Unit cell means "as Plexos reports it", which used to be the interval
        # unit ($, MW, lb). Monthly series come in coarser units ($000, GWh, ton), so
        # convert back to the interval unit to keep those rows on the scale they had.
        period_type = resolve_period_type(lookup_prop, class_name, parent_name, temporal_pattern, bool(is_rate))
        target_unit = _lookup_db_unit(base_dir, lookup_prop, class_name, parent_name, "interval") if period_type != "interval" else db_unit

    # Lookup in the provided df_units
    match = df_units[
        (df_units['UnitFrom'].str.lower() == db_unit.lower().strip()) & 
        (df_units['UnitTo'].str.lower() == target_unit.lower().strip())
    ]
    
    if not match.empty:
        factor = float(match.iloc[0]['ConversionRate'])
        print(f"    / Unit:  '{db_unit}' > '{target_unit}' | Factor Applied: {factor}")
        if pd.isna(factor):
            exceptions_report.record_nan_scale(lookup_prop, db_unit, target_unit)
        return factor, False
    else:
        print(f"    / Unit: No rule for '{db_unit}' > '{target_unit}'")
        # Same unit on both sides (or no target requested) needs no rule -- only a genuine
        # unit difference with no rule means the values silently stay in the wrong unit.
        needs_conversion = target_unit and db_unit and db_unit.lower().strip() != target_unit.lower().strip()
        if needs_conversion:
            exceptions_report.record_unit_miss(lookup_prop, db_unit, target_unit)
        return 1.0, True

def pull_pivoted_data(base_dir, property_name, unique_months, category_list=None, class_name=None, parent_name=None, is_rate=False, temporal_pattern="monthly", timeslice_name="All Periods"):
    """
    Executes a high-performance database PIVOT with case-insensitive and trailing-whitespace tolerant filters.
    
    Args:
        base_dir (str): The directory path where the Parquet data files are located.
        property_name (str): The specific metric to query (e.g., 'Electricity Consumption').
        unique_months (list): A list of expected time columns (e.g., ['Jan-2026', 'Feb-2026']) to ensure consistent schema.
        category_list (list/str, optional): A specific category or list of categories to filter by. Defaults to None.
        class_name (str, optional): The class of objects to filter for (e.g., 'Buildings'). Defaults to None.
        parent_name (str, optional): If provided, overrides settings to focus on nested data
        temporal_pattern (str, optional): Defines the aggregation level. Defaults to "monthly"; can be set to
            "monthly-summary", "daily", or "daily-summary" ("daily" and "daily-summary" both pull day-level granularity).
        timeslice_name (str,optional): which timeslice to pull the data from
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

    sub_conditions.append(f"LOWER(TRIM(f.TimesliceName)) = '{timeslice_name.lower().strip()}'")

    # Read one resolution only -- see resolve_period_type
    period_type = resolve_period_type(property_name, class_name, parent_name, temporal_pattern, bool(is_rate))
    sub_conditions.append(f"LOWER(TRIM(f.PeriodTypeName)) = '{period_type}'")

    master_filter = " AND ".join(sub_conditions)
    
    # Override filters if specifically looking for nested
    if parent_name:
        parent_filter = f"AND LOWER(TRIM(f.parentObjectName)) = '{parent_name.lower().strip()}'"
    else:
        parent_filter = ""

    # 3. Configure Temporal Granularity: Set SQL logic for daily vs monthly aggregation
    if temporal_pattern in ("daily", "daily-summary"):
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
              {parent_filter}
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

def apply_asset_mapping(df_pivoted, asset_mapping_df):
    if not asset_mapping_df or df_pivoted.empty:
        return df_pivoted
    
    # Here we map it, defaulting to its original name if no mapping is provided:
    df_pivoted['Object_Name'] = df_pivoted['Object_Name'].map(asset_mapping_df).fillna(df_pivoted['Object_Name'])
    
    # If multiple Plexos names map to one RTSim name, group them and sum their metrics
    # Identify value columns (everything except dimensions)
    dim_cols = [c for c in ['Object_Name', 'band_id', 'Year', 'Day_Id', 'Timeslice'] if c in df_pivoted.columns]
    val_cols = [c for c in df_pivoted.columns if c not in dim_cols]
    
    return df_pivoted.groupby(dim_cols, as_index=False)[val_cols].sum()