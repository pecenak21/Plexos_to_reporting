"""
transformers.py
Processes pivoted queries into standardized matrix visuals, handling flat, banded, and daily granularities.
"""
import pandas as pd
import numpy as np
import duckdb
import csv

# Note: Ensure BAND_MAP and BANDS_ORDERED are imported or defined as per your project
from database import pull_pivoted_data, get_automatic_scale_factor

def process_daily_block(parquet_base_dir, property_name, years, unique_months, class_name=None, is_rate=False, temporal_pattern="daily", asset_mapping=None):
    
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

    if asset_mapping:
        df_pivoted['Object_Name'] = df_pivoted['Object_Name'].map(asset_mapping).fillna(df_pivoted['Object_Name'])
        
        # If multiple Plexos names map to one RTSim name, group them and sum their metrics across dimensions
        dim_cols = ['Object_Name', 'band_id', 'Year', 'Day_Id']
        month_cols = [c for c in df_pivoted.columns if c not in dim_cols]
        df_pivoted = df_pivoted.groupby(dim_cols, as_index=False)[month_cols].sum()
    # --------------------------------------

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
        
        df_final = sub_table.reset_index()[sorted_cols + ['Day_Id']]
        
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


def process_emissions_block(parquet_base_dir, gas_name, target_header, years, unique_months, df_units, class_name, temporal_pattern, is_rate=False, explicit_unit=None, asset_mapping=None):

    # Existing functionality preserved
    df_pivoted = pull_pivoted_data(parquet_base_dir, 'Production', unique_months, emission_gas_name=gas_name, is_rate=False)
    if df_pivoted.empty: return pd.DataFrame()
    
    # Code to map the names to provided RTsim names
    if asset_mapping:
        df_pivoted['Object_Name'] = df_pivoted['Object_Name'].map(asset_mapping).fillna(df_pivoted['Object_Name'])
        
    df_pivoted = df_pivoted.groupby('Object_Name')[list(unique_months)].sum()

    scale_factor, _ = get_automatic_scale_factor(parquet_base_dir, target_header, df_units, explicit_unit=explicit_unit)
    df_pivoted = df_pivoted * scale_factor
    
    # Create an explicit copy so Pandas knows you own this data
    df_grid, _ = build_sum_totals(df_pivoted, years, unique_months)
    df_grid = df_grid.copy() 
    
    # Now you can safely set the index and the 'Total' row
    df_grid.loc['Total'] = df_grid.sum(axis=0)
    
    df_grid.index.name = ''
    # Logic for monthly-summary to filter only the total row
    if temporal_pattern == "monthly-summary":
        if 'Total' in df_grid.index:
            summary_row = df_grid.loc[['Total']].copy()
            summary_row.index = [f"{class_name}-{gas_name}-Total"]
            return summary_row

    df_grid.index.name = ''

    return df_grid

def process_flat_block(parquet_base_dir, property_name, header_name, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, temporal_pattern="monthly", timeslice_name="All Periods", explicit_unit=None, asset_mapping=None, parent_name=None,testy=False):

    df_pivoted = pull_pivoted_data(parquet_base_dir, property_name, unique_months, category_list=category_list, class_name=class_name, is_rate=is_rate, timeslice_name=timeslice_name, parent_name=parent_name)

    if df_pivoted.empty: 
        print(f"[DEBUG] ---> Result was EMPTY for property '{property_name}' under parent '{parent_name}'.")
        return pd.DataFrame()
    
    df_pivoted = pull_pivoted_data(parquet_base_dir, property_name, unique_months, category_list=category_list, class_name=class_name, is_rate=is_rate, timeslice_name=timeslice_name, parent_name=parent_name)

    if df_pivoted.empty: return pd.DataFrame()

    # Code to map the names to provided RTsim names
    if asset_mapping:
        df_pivoted['Object_Name'] = df_pivoted['Object_Name'].map(asset_mapping).fillna(df_pivoted['Object_Name'])
    
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

def process_ratings_block(parquet_base_dir, property_name, alias, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, timeslice_name="All Periods", explicit_unit=None, asset_mapping=None):
    # Reuse pull_pivoted_data since it fetches the raw matrix correctly
    df_pivoted = pull_pivoted_data(parquet_base_dir, property_name, unique_months, category_list=category_list, class_name=class_name, is_rate=is_rate, timeslice_name=timeslice_name)
    if df_pivoted.empty: return pd.DataFrame()
    
    # Code to map the names to provided RTsim names
    if asset_mapping:
        df_pivoted['Object_Name'] = df_pivoted['Object_Name'].map(asset_mapping).fillna(df_pivoted['Object_Name'])

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

def process_nested_block(parquet_base_dir, property_name, parent_name, child_name, header_name, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, temporal_pattern="monthly", timeslice_name="All Periods", explicit_unit=None, asset_mapping=None): 
    
    cat_items = category_list if isinstance(category_list, list) else [category_list]
    valid_cats = [str(cat).strip() for cat in cat_items if cat is not None and str(cat).lower().strip() != 'all']

    if valid_cats:
        placeholders = str(tuple(valid_cats)) if len(valid_cats) > 1 else f"('{valid_cats[0]}')"
        parent_query = f""" SELECT DISTINCT ParentObjectName FROM mem_fki WHERE ParentClassName = '{parent_name}' AND ParentObjectCategoryName IN {placeholders}"""
    else:
        parent_query = f"""SELECT DISTINCT ParentObjectName FROM mem_fki WHERE ParentClassName = '{parent_name}'"""

    result = duckdb.query(parent_query).df()
    
    # 2. Defensive check
    if result.empty or 'ParentObjectName' not in result.columns:
        print(f"Warning: Data not found in mem_fki. Columns found: {result.columns.tolist()}")
        return pd.DataFrame()
        
    all_parents = result['ParentObjectName'].tolist()

    mapped_parents = [asset_mapping.get(item, item) for item in all_parents]

    combined_rows = []
    for idx, parent in enumerate(all_parents): 
        print(parent_name)
        if parent_name == "Emission":
            sub_header = f"Total Effluents (lb) -- {mapped_parents[idx]}"
        else:
            sub_header = f"{mapped_parents[idx]}"

        df_data = process_flat_block(parquet_base_dir, property_name, header_name, years, unique_months, df_units, category_list=None, class_name=None, is_rate=is_rate, temporal_pattern=temporal_pattern, timeslice_name="All Periods", explicit_unit=explicit_unit, asset_mapping=asset_mapping, parent_name=parent)
        
        if not df_data.empty:
            df_data = df_data.reset_index()

            subheader_data = [sub_header] + [np.nan] * (len(df_data.columns) - 1)
            subheader_row = pd.DataFrame([subheader_data], columns=df_data.columns)

            spacer_data = [np.nan] * len(df_data.columns)
            spacer_df = pd.DataFrame([spacer_data], columns=df_data.columns)

            # Append subheader, pure numeric data, and spacer
            combined_rows.extend([subheader_row, df_data, spacer_df])
            
    # Return everything with a clean sequential index that you can completely drop on export
    return pd.concat(combined_rows, ignore_index=True) if combined_rows else pd.DataFrame()


    # bespoke code for fuels
def process_3_block(parquet_base_dir, parent_name, child_name, header_name, years, unique_months, df_units, category_list=None, class_name=None, is_rate=False, temporal_pattern="monthly", timeslice_name="All Periods", explicit_unit=None, asset_mapping=None):
    """
    Custom block generator for '( 3 ) Thermal Unit Fuel Use (MBTU)'
    Takes flat outputs for Fuel Offtake and Start Fuel Offtake and formats them 
    into the custom parent/sub-row structure without a bottom totals row.
    """
    # 1. Pull the flat block for "Fuel Offtake" across all generators
    df_fuel = process_flat_block(
        parquet_base_dir, "Fuel Offtake", header_name, years, unique_months, 
        df_units=df_units, category_list=category_list, class_name=class_name, is_rate=is_rate, 
        temporal_pattern=temporal_pattern, timeslice_name=timeslice_name, 
        explicit_unit=explicit_unit, asset_mapping=asset_mapping, parent_name=None
    )

    # 2. Pull the flat block for "Start Fuel Offtake" across all generators
    df_start = process_flat_block(
        parquet_base_dir, "Start Fuel Offtake", header_name, years, unique_months, 
        df_units=df_units, category_list=category_list, class_name=class_name, is_rate=is_rate, 
        temporal_pattern=temporal_pattern, timeslice_name=timeslice_name, 
        explicit_unit=explicit_unit, asset_mapping=asset_mapping, parent_name=None
    )

    if df_fuel.empty:
        return pd.DataFrame()

    # Drop any summary rows like 'Total' if present in the flat index
    if 'Total' in df_fuel.index:
        df_fuel = df_fuel.drop('Total', errors='ignore')
    if 'Total' in df_start.index:
        df_start = df_start.drop('Total', errors='ignore')

    # Convert dataframes to dictionaries for fast lookup by generator name
    fuel_dict = df_fuel.to_dict(orient='index')
    start_dict = df_start.to_dict(orient='index')

    month_cols = list(unique_months)
    combined_rows = []
    col_names = [''] + month_cols

    # Loop through each generator present in the Fuel Offtake dataset
    for gen_name in fuel_dict.keys():
        primary_vals = pd.Series(fuel_dict[gen_name]).reindex(month_cols, fill_value=0)
        startup_vals = pd.Series(start_dict.get(gen_name, {})) \
                       .reindex(month_cols, fill_value=0) if gen_name in start_dict else pd.Series(0, index=month_cols)
        
        secondary_vals = pd.Series(0, index=month_cols)
        topping_vals = pd.Series(0, index=month_cols)

        # Parent total is primary + startup (since secondary and topping are 0)
        parent_total = primary_vals + startup_vals

        # Construct rows matching your required format
        row_parent = [gen_name] + list(parent_total.values)
        row_prim   = ["        (Primary)"] + list(primary_vals.values)
        row_sec    = ["        (Secondary)"] + list(secondary_vals.values)
        row_start  = ["        (Startup)"] + list(startup_vals.values)
        row_top    = ["        (Topping)"] + list(topping_vals.values)

        block_df = pd.DataFrame([row_parent, row_prim, row_sec, row_start, row_top], columns=col_names)
        
        # Format matching your standard block output (Header row + Data + Spacer)
        header_vals = pd.DataFrame([col_names], columns=col_names)
        df_final = pd.concat([header_vals, block_df], ignore_index=True)
        
        spacer_df = pd.DataFrame([[''] * len(col_names)], columns=col_names)
        
        combined_rows.extend([df_final, spacer_df])

    return pd.concat(combined_rows, ignore_index=True) if combined_rows else pd.DataFrame()

def export_block_to_csv(file_handle, header_title, df_block):
    """
    Writes section titles, column headers, and pure numeric data directly 
    to a CSV file without turning floats into string objects.
    """
    writer = csv.writer(file_handle)
    
    # 1. Write Section Header (e.g., "( 1 ) System Summary")
    if header_title:
        writer.writerow([header_title])
    
    if not df_block.empty:
        # 2. Write Column Headers (e.g., Object_Name, Jan-26, Feb-26, ...)
        if isinstance(df_block.index, pd.MultiIndex):
            headers = list(df_block.index.names) + list(df_block.columns)
        else:
            headers = [(df_block.index.name or '')] + list(df_block.columns)
            
        writer.writerow(headers)
        
        # 3. Write Data Rows
        for idx, row in df_block.iterrows():
            idx_vals = list(idx) if isinstance(idx, tuple) else [idx]
            
            # Convert values: blank for NaN, float for numbers, string for labels
            formatted_values = []
            for v in row:
                if pd.isna(v):
                    formatted_values.append("")
                elif isinstance(v, (int, float, np.number)):
                    formatted_values.append(float(v)) # Output as unquoted number
                else:
                    formatted_values.append(str(v))
            
            writer.writerow(idx_vals + formatted_values)
            
    # 4. Write blank row spacer between sections
    writer.writerow([])