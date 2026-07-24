"""
transformers.py
Processes pivoted queries into standardized matrix visuals, handling flat, banded, and daily granularities.
"""
import pandas as pd
import numpy as np
import duckdb

# Note: Ensure BAND_MAP and BANDS_ORDERED are imported or defined as per your project
from database import pull_pivoted_data, get_automatic_scale_factor

def process_daily_block(parquet_base_dir, property_name, years, unique_months, class_name=None, is_rate=False, temporal_pattern="daily"):
    
    # 1. Pull the pivoted data
    df_pivoted = pull_pivoted_data(
        base_dir=parquet_base_dir, 
        class_name=class_name, 
        unique_months=unique_months, 
        property_name=property_name,
        is_rate=False,
        temporal_pattern=temporal_pattern
    )
    
    if df_pivoted is None or df_pivoted.empty:
        return pd.DataFrame() 

    # 2. Force consistency in types
    df_pivoted['Object_Name'] = df_pivoted['Object_Name'].astype(str)
    df_pivoted['band_id'] = df_pivoted['band_id'].astype(int)
    df_pivoted['Year'] = df_pivoted['Year'].astype(int)
    df_pivoted['Day_Id'] = df_pivoted['Day_Id'].astype(int)

    # 3. Densification
    df_indexed = df_pivoted.set_index(['Object_Name', 'band_id', 'Year', 'Day_Id'])
    if not df_indexed.index.is_unique:
        df_indexed = df_indexed.groupby(level=[0, 1, 2, 3]).sum()

    full_index = pd.MultiIndex.from_product(
        [df_indexed.index.get_level_values('Object_Name').unique(), 
         df_indexed.index.get_level_values('band_id').unique(), 
         df_indexed.index.get_level_values('Year').unique(), 
         range(1, 32)], 
        names=['Object_Name', 'band_id', 'Year', 'Day_Id']
    )
    df_dense = df_indexed.reindex(full_index, fill_value=0.0).reset_index()

    month_cols = [c for c in df_dense.columns if c not in ['Object_Name', 'band_id', 'Year', 'Day_Id']]
    df_dense = df_dense.groupby(['Object_Name', 'band_id', 'Day_Id'])[month_cols].sum().reset_index()

    # 4. Calculate Totals
    df_work = df_dense.copy()
    for yr in years:
        yr_months = [m for m in unique_months if f"-{yr}" in m]
        df_work[f"Tot-{yr}"] = df_work[yr_months].sum(axis=1)
    
    total_cols = [c for c in df_work.columns if c.startswith('Tot-')]
    df_work['Total'] = df_work[total_cols].sum(axis=1)
    
    # 5. Define sorting logic and columns
    final_report_cols = [c for c in df_work.columns if c not in ['Object_Name', 'band_id', 'Day_Id']]
    
    def sort_key(x):
        if x == 'Total':
            return pd.Timestamp('9999-12-31')
        if x.startswith('Tot-'):
            year = x.split('-')[1]
            return pd.to_datetime(f'Dec-31-{year}')
        return pd.to_datetime(x, format='%b-%Y')

    sorted_cols = sorted(final_report_cols, key=sort_key)
    
    # 6. Format into "Sub-table" structure
    all_chunks = []
    for asset, group in df_work.groupby(['Object_Name']):
        sub_table = group.set_index('Day_Id')[sorted_cols]
        
        # Prepare data: header row + data
        header_vals = pd.DataFrame([sorted_cols], columns=sorted_cols)
        data_vals = sub_table.reset_index()
        
        # Combine and FORCE column order
        df_final = pd.concat([header_vals, data_vals], ignore_index=True)
        df_final = df_final[sorted_cols + ['Day_Id']] 
        
         # Modify index
        new_index = df_final.index.tolist()
        new_index[0] = " " 
        df_final.index = new_index
        
        # Create header and spacer
        header_row = pd.DataFrame(
            [[np.nan] * (len(sorted_cols) + 1)], 
            index=[f"{asset[0]}"], 
            columns=sorted_cols + ['Day_Id']
        ).fillna("") 
        
        spacer = pd.DataFrame(
            [[np.nan] * (len(sorted_cols) + 1)], 
            index=[''], 
            columns=sorted_cols + ['Day_Id']
        ).fillna("")
        
        block = pd.concat([header_row, df_final], axis=0)
        all_chunks.append(pd.concat([block, spacer], axis=0))
    
    return pd.concat(all_chunks)


def process_emissions_block(parquet_base_dir, gas_name, target_header, years, unique_months, df_units, class_name, temporal_pattern, is_rate=False, explicit_unit=None):

    # Existing functionality preserved
    df_pivoted = pull_pivoted_data(parquet_base_dir, 'Production', unique_months, emission_gas_name=gas_name, is_rate=False)
    if df_pivoted.empty: return pd.DataFrame()
    
    df_pivoted = df_pivoted.groupby('Object_Name')[list(unique_months)].sum()
    scale_factor, _ = get_automatic_scale_factor(parquet_base_dir, target_header, df_units, explicit_unit=explicit_unit)
    df_pivoted = df_pivoted * scale_factor
    
    # Create an explicit copy so Pandas knows you own this data
    df_grid, _ = build_sum_totals(df_pivoted, years, unique_months)
    df_grid = df_grid.copy() 
    
    # Now you can safely set the index and the 'Total' row
    df_grid.loc['Total'] = df_grid.sum(axis=0)
    # --- FIX ENDS HERE ---
    
    df_grid.index.name = ''
    # Logic for monthly-summary to filter only the total row
    if temporal_pattern == "monthly-summary":
        if 'Total' in df_grid.index:
            summary_row = df_grid.loc[['Total']].copy()
            summary_row.index = [f"{class_name}-{gas_name}-Total"]
            return summary_row

    df_grid.index.name = ''

    return df_grid

def process_flat_block(parquet_base_dir, property_name, header_name, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, temporal_pattern="monthly", timeslice_name="All Periods", explicit_unit=None):
    df_pivoted = pull_pivoted_data(parquet_base_dir, property_name, unique_months, category_list=category_list, class_name=class_name, is_rate=is_rate, timeslice_name=timeslice_name)
    if df_pivoted.empty: return pd.DataFrame()
    df_pivoted = df_pivoted.groupby('Object_Name')[list(unique_months)].sum()
    
    # Pass explicit_unit instead of header_name to your scale factor function
    scale_factor, _ = get_automatic_scale_factor(parquet_base_dir, property_name, df_units, explicit_unit=explicit_unit)
    df_pivoted = df_pivoted * scale_factor
    
    # When creating df_grid, ensure it's a fresh object
    if is_rate:
        df_grid, _ = build_rate_totals(df_pivoted, years, unique_months)
        df_grid = df_grid.copy()
        df_grid.loc['Total'] = df_grid.replace(0, np.nan).mean(axis=0).fillna(0)
    else:
        df_grid, _ = build_sum_totals(df_pivoted, years, unique_months)
        df_grid = df_grid.copy()
        df_grid.loc['Total'] = df_grid.sum(axis=0)
    
    # Logic for monthly-summary to filter only the total row
    if temporal_pattern == "monthly-summary":
        if 'Total' in df_grid.index:
            summary_row = df_grid.loc[['Total']].copy()
            cat_label = str(category_list).replace('[','').replace(']','').replace("'",'').replace(", ", "-") if category_list else "all"
            summary_row.index = [f"{class_name}-{cat_label}-{property_name}-Total"]
            return summary_row

    df_grid.index.name = ''
    return df_grid

def process_ratings_block(parquet_base_dir, property_name, alias, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, timeslice_name="All Periods", explicit_unit=None):
    # Reuse pull_pivoted_data since it fetches the raw matrix correctly
    df_pivoted = pull_pivoted_data(parquet_base_dir, property_name, unique_months, category_list=category_list, class_name=class_name, is_rate=is_rate, timeslice_name=timeslice_name)
    if df_pivoted.empty: return pd.DataFrame()
    
    df_pivoted = df_pivoted.groupby('Object_Name')[list(unique_months)].sum()
    
    # Apply automatic unit scaling
    scale_factor, _ = get_automatic_scale_factor(parquet_base_dir, property_name, df_units, explicit_unit=explicit_unit)
    df_pivoted = df_pivoted * scale_factor
    
    # Build totals grid without keeping intermediate total rows
    if is_rate:
        df_grid, _ = build_rate_totals(df_pivoted, years, unique_months)
        df_grid = df_grid.copy()
        df_grid.loc['Total'] = df_grid.replace(0, np.nan).mean(axis=0).fillna(0)
    else:
        df_grid, _ = build_sum_totals(df_pivoted, years, unique_months)
        df_grid = df_grid.copy()
        df_grid.loc['Total'] = df_grid.sum(axis=0)
        
    # Drop the 'Total' row so it doesn't get repeated between properties
    if 'Total' in df_grid.index:
        df_grid = df_grid.drop('Total')
        
    # Append the alias/unit to each item name in the index (e.g., "Arlington A:MW")
    if alias and str(alias).strip().lower() != 'nan':
        df_grid.index = [f"{idx}:{alias}" for idx in df_grid.index]
        
    df_grid.index.name = ''
    return df_grid

def build_sum_totals(df_pivot, years, unique_months):
    final_columns = []
    grand_total_series = pd.Series(0.0, index=df_pivot.index)
    for yr in years:
        yr_months = [m for m in unique_months if f"-{yr}" in m]
        final_columns.extend(yr_months)
        yr_total_col = f"Tot-{yr}"
        df_pivot[yr_total_col] = df_pivot[yr_months].sum(axis=1)
        final_columns.append(yr_total_col)
        grand_total_series += df_pivot[yr_total_col]
    df_pivot['Total'] = grand_total_series
    final_columns.append('Total')
    return df_pivot[final_columns], final_columns

def build_rate_totals(df_pivot, years, unique_months):
    final_columns = []
    for yr in years:
        yr_months = [m for m in unique_months if f"-{yr}" in m]
        final_columns.extend(yr_months)
        yr_total_col = f"Tot-{yr}"
        df_pivot[yr_total_col] = df_pivot[yr_months].replace(0, np.nan).mean(axis=1).fillna(0)
        final_columns.append(yr_total_col)
    df_pivot['Total'] = df_pivot[unique_months].replace(0, np.nan).mean(axis=1).fillna(0)
    final_columns.append('Total')
    return df_pivot[final_columns], final_columns

def build_combined_emissions_section(parquet_base_dir, topline_header, years, unique_months, df_units, class_name=None, temporal_pattern="monthly", is_rate=False, explicit_unit=None):
    
    # Dynamically find gases
    gas_query = "SELECT DISTINCT ParentObjectName FROM mem_fki WHERE ParentClassName = 'Emission'"
    result = duckdb.query(gas_query).df()
    
    # 2. Defensive check
    if result.empty or 'ParentObjectName' not in result.columns:
        print(f"Warning: No emission gases found in mem_fki. Columns found: {result.columns.tolist()}")
        return pd.DataFrame()
        
    all_gases = result['ParentObjectName'].tolist()
    
    combined_rows = []
    for gas in sorted(all_gases): 
        sub_header = f"Total Effluents (lb) -- {gas}"
        # Pass the pattern through to the processor
        df_gas = process_emissions_block(parquet_base_dir, gas, topline_header, years, unique_months, df_units, class_name, temporal_pattern,explicit_unit=explicit_unit)
                
        if not df_gas.empty:
            df_gas = df_gas.reset_index()

            header_vals = pd.DataFrame([df_gas.columns], columns=df_gas.columns)
            df_final = pd.concat([header_vals, df_gas], ignore_index=True)

            subheader_row = pd.DataFrame(index=[sub_header], columns=df_gas.columns)
            spacer_df = pd.DataFrame(index=[''], columns=df_gas.columns)
            
            combined_rows.extend([subheader_row, df_final, spacer_df])
            
    return pd.concat(combined_rows) if combined_rows else pd.DataFrame()