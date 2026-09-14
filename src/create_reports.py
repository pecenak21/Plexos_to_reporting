import os
import sys
import pandas as pd
import duckdb
from collections import defaultdict
from convert_zip_to_parquet import convert_zip_to_parquet
from transformers import (export_block_to_csv, process_flat_block, process_daily_block, process_nested_block, process_ratings_block, process_3_block, process_23_block, process_32_block)
from standard_integration_testing import run_sit_validation
from database import initialize_database_structures
import exceptions_report

def load_excel_config(config_path):
    xl = pd.ExcelFile(config_path)
    
    # 1. Load Standard Blueprint (Expected: Header, Class, Group, Property, Pattern, Rate, Unit, Sign)
    blueprint = []
    if 'Blueprint_std' in xl.sheet_names:
        df_bp = pd.read_excel(xl, 'Blueprint_std')
        df_bp.columns = df_bp.columns.astype(str).str.strip().str.title()
        expected_std = ['Header', 'Class', 'Group', 'Property', 'Pattern', 'Rate', 'Unit', 'Sign']
        for col in expected_std:
            if col not in df_bp.columns:
                df_bp[col] = ''
        # Sign flips reporting convention (RTSim shows purchases as negative); blank means +1
        df_bp['Sign'] = pd.to_numeric(df_bp['Sign'], errors='coerce').fillna(1)
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
    script_path = df_summary.loc['ScriptPath', 'Value']
    cli_path = df_summary.loc['CLI_Path', 'Value']
    script_path = script_path.split('src')[0]
    base_output_path = df_summary.loc['OutputPath', 'Value']
    overwrite_yn = df_summary.loc['Overwrite_Parquet', 'Value']
    integration_test_yn = df_summary.loc['Run_Integration_Test', 'Value']

    # Load UnitConversion
    df_units = pd.read_excel(xl, 'UnitConversion')
    df_units['UnitFrom'] = df_units['UnitFrom'].astype(str).str.strip()
    df_units['UnitTo'] = df_units['UnitTo'].astype(str).str.strip()
    df_units['ConversionRate'] = pd.to_numeric(df_units['ConversionRate'])

    df_map = pd.read_excel(xl, 'Generator_name_map')
    asset_mapping = dict(zip(df_map['Resources_Plexos'], df_map['Resources_RTSim']))
    
    # Section 23 contract table: (Plexos fuel, RTSim report label, MMBtu -> contract unit factor).
    # Labels are kept unstripped -- RTSim's row labels are fixed-width and the padding is significant.
    contract_rows = []
    if 'Contract_name_map' in xl.sheet_names:
        df_contracts = pd.read_excel(xl, 'Contract_name_map')
        for plexos, label, factor in zip(df_contracts['Resources_Plexos'], df_contracts['Report_Label'],
                                         df_contracts['ConversionFactor']):
            if pd.isna(plexos) or not str(plexos).strip():
                continue
            label = '' if pd.isna(label) else str(label)
            contract_rows.append((str(plexos).strip(), label, pd.to_numeric(factor, errors='coerce')))

    return blueprint, blueprint_rat, asset_groups, input_path, cli_path, base_output_path, df_units, overwrite_yn, integration_test_yn, script_path, asset_mapping, contract_rows


def execute_standard_report(parquet_base_dir, blueprint, asset_groups, output_path, years, unique_months, df_units, asset_mapping, contract_map=()):
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
            _, class_input, group_input, prop_input, temp_pattern, is_rate, unit_val, sign = row

            c_in = str(class_input).strip()
            g_in = str(group_input).strip()
            target_categories = asset_groups.get((c_in, g_in), None)
            is_banded = False
            nested=False
            parent_in = c_in
            child_in = ""
             
            if '.' in c_in:
                nested=True
                parent_in=c_in.split('.')[0]
                child_in=c_in.split('.')[1]
                target_categories = asset_groups.get((parent_in, g_in), None)
            
            if header == "( 3 ) Thermal Unit Fuel Use (MBTU)":
                print(f"Note: Custom Code to match RTSim output")
                df_block = process_3_block(
                    parquet_base_dir, parent_in, child_in, header, years, unique_months, 
                    df_units=df_units, category_list=target_categories, 
                    class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern,
                    explicit_unit=unit_val, asset_mapping=asset_mapping
                )
                idx_flag, header_flag = False, False

            elif header.startswith("( 23 )"):
                print(f"Note: Custom Code to match RTSim output")
                df_block = process_23_block(parquet_base_dir, years, unique_months, contract_map)
                idx_flag, header_flag = True, True

            elif header == "( 32 ) Total Effluents by Type lbs":
                print(f"Note: Custom Code to match RTSim output")
                df_block = process_32_block(
                    parquet_base_dir, prop_input, parent_in, child_in, header, years, unique_months,
                    df_units=df_units, category_list=target_categories,
                    class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern,
                    explicit_unit=unit_val, asset_mapping=asset_mapping
                )
                idx_flag, header_flag = False, False

            elif temp_pattern in ("daily", "daily-summary"):
                df_block = process_daily_block(parquet_base_dir, prop_input, years, unique_months, class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern, asset_mapping=asset_mapping)
                idx_flag, header_flag = True, False
            else:
                if nested:
                    df_block = process_nested_block(
                        parquet_base_dir, prop_input, parent_in, child_in, header, years, unique_months, 
                        df_units=df_units, category_list=target_categories, 
                        class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern,
                        explicit_unit=unit_val, asset_mapping=asset_mapping
                    )
                    idx_flag, header_flag = False, False

                else:
                    df_block = process_flat_block(
                        parquet_base_dir, prop_input, header, years, unique_months, 
                        df_units=df_units, category_list=target_categories, 
                        class_name=c_in, is_rate=is_rate, temporal_pattern=temp_pattern,
                        explicit_unit=unit_val, asset_mapping=asset_mapping
                    )
                    idx_flag, header_flag = True, True
                
            if df_block is not None and not df_block.empty:
                print(f"    - Data retrieved for: {prop_input}")
                if sign != 1:
                    # Bespoke/nested blocks carry label and header strings, so only flip numeric cells
                    df_block = df_block.copy()
                    for col in df_block.columns:
                        numeric = pd.to_numeric(df_block[col], errors='coerce')
                        mask = numeric.notna()
                        # + 0.0 turns the -0.0 produced by flipping a zero back into 0.0
                        df_block.loc[mask, col] = numeric[mask] * sign + 0.0
                blocks_for_header.append(df_block)
            else:
                print(f"    - [!] No data returned for: {prop_input}")
                exceptions_report.record_no_data(header, prop_input, c_in)

        # Several flat blocks under one header each bring their own Total row; RTSim shows
        # a single Total for the whole section, so replace them with one recomputed at the end.
        if len(blocks_for_header) > 1 and all('Total' in b.index for b in blocks_for_header):
            body = pd.concat([b.drop(index='Total') for b in blocks_for_header], axis=0)
            header_is_rate = all(str(r[5]).strip().lower() == 'true' for r in row_entries)
            total = body.where(body != 0).mean(axis=0).fillna(0) if header_is_rate else body.sum(axis=0)
            blocks_for_header = [body, total.to_frame('Total').T]

        if blocks_for_header:
            compiled_sections.append((header, pd.concat(blocks_for_header, axis=0), idx_flag, header_flag))

    print(f"[+] Writing standard report to: {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for header, df_block, idx_flag, header_flag in compiled_sections:
            export_block_to_csv(
                f, 
                header_title=header, 
                df_block=df_block, 
                include_index=idx_flag, 
                include_header=header_flag
            )

def execute_timeslice_report(parquet_base_dir, blueprint_rat, asset_groups, output_path, years, unique_months, df_units, asset_mapping=None):
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
                explicit_unit=unit_val, asset_mapping=asset_mapping
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
        for title, df_block, _, _ in compiled_sections:
            export_block_to_csv(f, header_title=title, df_block=df_block)

def execute_pipeline(config_path):
    print(f"[+] Initializing report generation from: {config_path}")
    exceptions_report.reset()
    blueprint, blueprint_rat, asset_groups, input_path, cli_path, dir_name, df_units, overwrite, run_testing, script_path, asset_mapping, contract_rows = load_excel_config(config_path)

    parquet_path_out=os.path.join(dir_name, "Parquet Files")

    parquet_base_dir = convert_zip_to_parquet(input_path, cli_path=cli_path, output_dir=parquet_path_out, overwrite=overwrite)
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

    os.makedirs(dir_name, exist_ok=True)

    print("[+] Validating workbook configuration against the solution...")
    initialize_database_structures(parquet_base_dir)
    exceptions_report.validate_name_map(asset_mapping)
    exceptions_report.validate_unit_table(df_units)
    exceptions_report.validate_blueprint(blueprint, asset_groups)
    exceptions_report.validate_contract_map(contract_rows)

    # Execute Standard Report if blueprint is provided
    if blueprint:
        std_output_path = os.path.join(dir_name, "Standard_Report.csv")
        contract_map = [(plexos, label, factor) for plexos, label, factor in contract_rows if label.strip()]
        execute_standard_report(parquet_base_dir, blueprint, asset_groups, std_output_path, years, unique_months, df_units, asset_mapping, contract_map)
        
    # Execute Timeslice Report if blueprint_rat is provided
    if blueprint_rat:
        rat_output_path = os.path.join(dir_name, "Ratings_Report.csv")
        execute_timeslice_report(parquet_base_dir, blueprint_rat, asset_groups, rat_output_path, years, unique_months, df_units, asset_mapping)
        
    print("[+] All report generation complete.")

    # Written before SIT runs -- when SIT fails, these exceptions are usually the reason
    exceptions_report.write(dir_name)

    if run_testing:
        baseline_dir = f"{script_path}/docs/Baseline Reports"
        
        passed = run_sit_validation(baseline_dir, dir_name)
        if not passed:
            raise RuntimeError("SIT validation failed against baseline reports.")
        
    print("[+] Report testing complete.")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'report_config.xlsx'
    execute_pipeline(config_path)