import sys
import pandas as pd
import duckdb
from collections import defaultdict
from convert_zip_to_parquet import convert_zip_to_parquet
from transformers import (
    process_flat_block, process_banded_block, 
    process_daily_block, build_combined_emissions_section
)

def load_excel_config(config_path):
    xl = pd.ExcelFile(config_path)
    
    # Load Blueprint
    df_bp = pd.read_excel(xl, 'Blueprint')
    blueprint = [tuple(x) for x in df_bp.to_numpy()]
    
    # Load Groups and handle list parsing safely
    df_grps = pd.read_excel(xl, 'Groups', header=0)
    df_grps['Class'] = df_grps['Class'].astype(str).str.strip()
    df_grps['Group'] = df_grps['Group'].astype(str).str.strip()
    
    # Convert comma-separated string to list, ignoring empty/None values
    df_grps['Assets'] = df_grps['Assets'].astype(str).apply(
        lambda x: [item.strip() for item in x.split(',')] if x != 'nan' else []
    )
    
    asset_groups = df_grps.set_index(['Class', 'Group'])['Assets'].to_dict()
    
    # Load Paths
    df_summary = pd.read_excel(xl, 'Summary', index_col=0)
    input_path = df_summary.loc['InputPath', 'Value']
    output_path = df_summary.loc['OutputPath', 'Value']
    overwrite_yn = df_summary.loc['Overwrite', 'Value']

    # Load UnitConversion
    df_units = pd.read_excel(xl, 'UnitConversion')
    # Clean up the data once here so it is ready for lookup
    df_units['UnitFrom'] = df_units['UnitFrom'].astype(str).str.strip()
    df_units['UnitTo'] = df_units['UnitTo'].astype(str).str.strip()
    df_units['ConversionRate'] = pd.to_numeric(df_units['ConversionRate'])
    
    return blueprint, asset_groups, input_path, output_path, df_units, overwrite_yn

def execute_pipeline(config_path):
    print(f"[+] Initializing report generation from: {config_path}")
    blueprint, asset_groups, input_path, output_path, df_units, overwrite = load_excel_config(config_path)
    
    parquet_base_dir = convert_zip_to_parquet(input_path, overwrite=overwrite)
    if parquet_base_dir is None: return
    
    base_dir_clean = str(parquet_base_dir).replace('\\', '/')
    period_path = f"{base_dir_clean}/period/**/*.parquet"
    
    # Get time dimensions
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
    
    grouped_blueprint = defaultdict(list)
    for entry in blueprint:
        grouped_blueprint[entry[0]].append(entry)
        
    compiled_sections = []
    print("[+] Beginning processing sequence...")
    
    for header, row_entries in grouped_blueprint.items():
        blocks_for_header = []
        idx_flag = True
        
        print(f"[+] Processing section: {header}")
        
        for _, class_input, group_input, prop_input, temp_pattern, is_rate in row_entries:
            c_in = str(class_input).strip()
            g_in = str(group_input).strip()
            target_categories = asset_groups.get((c_in, g_in), None)

            #This code is not implemented yet, until I hear from Jim on bands
            is_banded=False
            
            # Select appropriate processing function
            if c_in == "Emission":
                df_block = build_combined_emissions_section(parquet_base_dir, header, years, unique_months, df_units=df_units,class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern)
                idx_flag = True
                header_flag=False
            elif temp_pattern == "daily":
                df_block = process_daily_block(parquet_base_dir, prop_input, years, unique_months,   class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern)
                idx_flag = True
                header_flag=False
            elif is_banded:
                df_block = process_banded_block(parquet_base_dir, prop_input, header, years, unique_months, category_list=target_categories, class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern)
                idx_flag = False
                header_flag=True
            else:
                df_block = process_flat_block(parquet_base_dir, prop_input, header, years, unique_months, df_units=df_units,  category_list=target_categories, class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern)
                idx_flag = True
                header_flag=True
                
            
            # Check for data presence and log status
            if df_block is not None and not df_block.empty:
                print(f"    - Data retrieved for: {prop_input}")
                blocks_for_header.append(df_block)
            else:
                print(f"    - [!] No data returned for: {prop_input}")
        
        if blocks_for_header:
            compiled_sections.append((header, pd.concat(blocks_for_header, axis=0), idx_flag, header_flag))
        else:
            print(f"    [!] Section '{header}' contained no valid data records.")
    df_block.to_csv(r"C:\Users\pecen\Downloads\test_df.csv",header=False)
    # Export to output
    print(f"[+] Writing final report to: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for header, df_block, idx_flag, header_flag in compiled_sections:
            f.write(f"{header}\n")
            df_block.to_csv(f, index=idx_flag, header=header_flag, lineterminator='\n')
            f.write("\n\n")
            
    print("[+] Report generation complete.")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'report_config.xlsx'
    execute_pipeline(config_path)