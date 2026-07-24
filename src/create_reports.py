import os
import sys
import pandas as pd
import duckdb
from collections import defaultdict
from convert_zip_to_parquet import convert_zip_to_parquet
from transformers import (process_flat_block, process_daily_block, build_combined_emissions_section, process_ratings_block)

def load_excel_config(config_path):
    xl = pd.ExcelFile(config_path)
    
    # 1. Load Standard Blueprint (Expected: Header, Class, Group, Property, Pattern, Rate, Unit)
    blueprint = []
    if 'Blueprint_std' in xl.sheet_names:
        df_bp = pd.read_excel(xl, 'Blueprint_std')
        df_bp.columns = df_bp.columns.astype(str).str.strip().str.title()
        expected_std = ['Header', 'Class', 'Group', 'Property', 'Pattern', 'Rate', 'Unit']
        for col in expected_std:
            if col not in df_bp.columns:
                df_bp[col] = ''
        blueprint = [tuple(x) for x in df_bp[expected_std].to_numpy()]

    # 2. Load Timeslice Blueprint (Blueprint_RAT)
    blueprint_rat = []
    if 'Blueprint_rat' in xl.sheet_names:
        df_rat = pd.read_excel(xl, 'Blueprint_rat')
        df_rat.columns = df_rat.columns.astype(str).str.strip().str.title()
        expected_rat = ['Class', 'Group', 'Property', 'Alias', 'Unit']
        for col in expected_rat:
            if col not in df_rat.columns:
                df_rat[col] = ''
        blueprint_rat = [tuple(x) for x in df_rat[expected_rat].to_numpy()]
    
    # Load Groups and handle list parsing safely
    df_grps = pd.read_excel(xl, 'Groups', header=0)
    df_grps['Class'] = df_grps['Class'].astype(str).str.strip()
    df_grps['Group'] = df_grps['Group'].astype(str).str.strip()
    df_grps['Assets'] = df_grps['Assets'].astype(str).apply(
        lambda x: [item.strip() for item in x.split(',')] if x != 'nan' else []
    )
    asset_groups = df_grps.set_index(['Class', 'Group'])['Assets'].to_dict()
    
    # Load Paths & Settings
    df_summary = pd.read_excel(xl, 'Summary', index_col=0)
    input_path = df_summary.loc['InputPath', 'Value']
    base_output_path = df_summary.loc['OutputPath', 'Value']
    overwrite_yn = df_summary.loc['Overwrite', 'Value']

    # Load UnitConversion
    df_units = pd.read_excel(xl, 'UnitConversion')
    df_units['UnitFrom'] = df_units['UnitFrom'].astype(str).str.strip()
    df_units['UnitTo'] = df_units['UnitTo'].astype(str).str.strip()
    df_units['ConversionRate'] = pd.to_numeric(df_units['ConversionRate'])
    
    return blueprint, blueprint_rat, asset_groups, input_path, base_output_path, df_units, overwrite_yn


def execute_standard_report(parquet_base_dir, blueprint, asset_groups, output_path, years, unique_months, df_units):
    print("[+] Building Standard Report...")
    grouped_blueprint = defaultdict(list)
    for entry in blueprint:
        header_key = entry[0]
        grouped_blueprint[header_key].append(entry)
        
    compiled_sections = []
    for header, row_entries in grouped_blueprint.items():
        blocks_for_header = []
        idx_flag = True
        
        print(f"[+] Processing section: {header}")
        for row in row_entries:
            # Unpack all 7 columns safely: Header, Class, Group, Property, Pattern, Rate, Unit
            _, class_input, group_input, prop_input, temp_pattern, is_rate, unit_val = row

            c_in = str(class_input).strip()
            g_in = str(group_input).strip()
            target_categories = asset_groups.get((c_in, g_in), None)
            is_banded = False
            
            if c_in == "Emission":
                df_block = build_combined_emissions_section(parquet_base_dir, header, years, unique_months, df_units=df_units, class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern, explicit_unit=unit_val)
                idx_flag, header_flag = True, False
            elif temp_pattern == "daily":
                df_block = process_daily_block(parquet_base_dir, prop_input, years, unique_months, class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern)
                idx_flag, header_flag = True, False
            else:
                df_block = process_flat_block(
                    parquet_base_dir, prop_input, header, years, unique_months, 
                    df_units=df_units, category_list=target_categories, 
                    class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern,
                    explicit_unit=unit_val
                )
                idx_flag, header_flag = True, True
                
            if df_block is not None and not df_block.empty:
                print(f"    - Data retrieved for: {prop_input}")
                blocks_for_header.append(df_block)
            else:
                print(f"    - [!] No data returned for: {prop_input}")
        
        if blocks_for_header:
            compiled_sections.append((header, pd.concat(blocks_for_header, axis=0), idx_flag, header_flag))

    print(f"[+] Writing standard report to: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for header, df_block, idx_flag, header_flag in compiled_sections:
            f.write(f"{header}\n")
            df_block.to_csv(f, index=idx_flag, header=header_flag, lineterminator='\n')
            f.write("\n\n")


def execute_timeslice_report(parquet_base_dir, blueprint_rat, asset_groups, output_path, years, unique_months, df_units):
    print("[+] Building Timeslice Report...")
    timeslice_query = "SELECT DISTINCT TimesliceName FROM mem_fki ORDER BY TimesliceId"
    timeslices = duckdb.query(timeslice_query).df()['TimesliceName'].tolist()
    
    compiled_sections = []
    for ts_name in timeslices:
        print(f"[+] Processing Timeslice Section: {ts_name}")
        
        blocks_for_timeslice = []
        for c_in, g_in, prop_input, alias, unit_val in blueprint_rat:
            target_categories = asset_groups.get((c_in, g_in), None)
            
            # Use our dedicated ratings block builder
            df_block = process_ratings_block(
                parquet_base_dir=parquet_base_dir, 
                property_name=prop_input, 
                alias=alias, 
                years=years, 
                unique_months=unique_months, 
                df_units=df_units, 
                category_list=target_categories,
                class_name=c_in,
                timeslice_name=ts_name,
                explicit_unit=unit_val
            )
            
            if df_block is not None and not df_block.empty:
                print(f"    - Data retrieved for: {prop_input} ({alias})")
                blocks_for_timeslice.append(df_block)
            else:
                print(f"    - [!] No data returned for: {prop_input}")
                
        if blocks_for_timeslice:
            # Concatenate all properties for this timeslice together contiguously
            combined_ts_df = pd.concat(blocks_for_timeslice, axis=0)
            compiled_sections.append((ts_name, combined_ts_df, True, True))

    print(f"[+] Writing Timeslice report to: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for title, df_block, idx_flag, header_flag in compiled_sections:
            if title:
                f.write(f"{title}\n")
            if not df_block.empty:
                df_block.to_csv(f, index=idx_flag, header=header_flag, lineterminator='\n')
            f.write("\n")

def execute_pipeline(config_path):
    print(f"[+] Initializing report generation from: {config_path}")
    blueprint, blueprint_rat, asset_groups, input_path, base_output_path, df_units, overwrite = load_excel_config(config_path)

    parquet_base_dir = convert_zip_to_parquet(input_path, overwrite=overwrite)
    if parquet_base_dir is None: return
    
    base_dir_clean = str(parquet_base_dir).replace('\\', '/')
    period_path = f"{base_dir_clean}/period/**/*.parquet"
    
    time_df = duckdb.query(f"""
        SELECT DISTINCT 
            CAST(EXTRACT(YEAR FROM CAST(StartDate AS TIMESTAMP)) AS INTEGER) AS Year, 
            strftime(CAST(StartDate AS TIMESTAMP), '%b-%Y') AS Month_Label, 
            CAST(StartDate AS TIMESTAMP) as raw_date 
        FROM read_parquet('{period_path}') 
        ORDER BY raw_date
    """).df()
    
    years = sorted(time_df['Year'].unique())
    unique_months = time_df['Month_Label'].unique()
    
    # Split the base output path to append unique hardcoded filenames
    dir_name = os.path.dirname(base_output_path)
    
    # Execute Standard Report if blueprint is provided
    if blueprint:
        std_output_path = os.path.join(dir_name, "Standard_Report.csv")
        execute_standard_report(parquet_base_dir, blueprint, asset_groups, std_output_path, years, unique_months, df_units)
        
    # Execute Timeslice Report if blueprint_rat is provided
    if blueprint_rat:
        rat_output_path = os.path.join(dir_name, "Ratings_Report.csv")
        execute_timeslice_report(parquet_base_dir, blueprint_rat, asset_groups, rat_output_path, years, unique_months, df_units)
        
    print("[+] All report generation complete.")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'report_config.xlsx'
    execute_pipeline(config_path)