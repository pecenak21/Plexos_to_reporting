import pandas as pd
import numpy as np
import os
import io
import sys
from datetime import datetime

class TeeLogger:
    """Helper class to simultaneously print to the terminal and write to a log file."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def close(self):
        self.log.close()

def parse_report_into_sections(filepath):
    sections = {}
    current_header = None
    current_lines = []
    
    if not os.path.exists(filepath):
        print(f"  [!] Warning: File not found -> {filepath}")
        return sections

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            
            if ',' not in stripped and (stripped.startswith('(') or not current_lines):
                if current_header and current_lines:
                    try:
                        df = pd.read_csv(io.StringIO(''.join(current_lines)), index_col=0)
                    except Exception:
                        df = pd.read_csv(io.StringIO(''.join(current_lines)))
                    sections[current_header] = df
                    current_lines = []
                current_header = stripped
            else:
                current_lines.append(line)
                
    if current_header and current_lines:
        try:
            df = pd.read_csv(io.StringIO(''.join(current_lines)), index_col=0)
        except Exception:
            df = pd.read_csv(io.StringIO(''.join(current_lines)))
        sections[current_header] = df
        
    return sections

def compare_report_files(golden_path, generated_path, report_name="Report", tolerance=1e-5):
    print(f"\n[+] Running SIT Semantic Diff for: {report_name}")
    print(f"    Baseline:  {golden_path}")
    print(f"    Generated: {generated_path}")
    
    golden_sections = parse_report_into_sections(golden_path)
    gen_sections = parse_report_into_sections(generated_path)
    
    if not golden_sections or not gen_sections:
        print(f"  [FAIL] Could not parse sections for {report_name}.")
        return False
        
    differences_found = False
    all_headers = sorted(set(golden_sections.keys()).union(set(gen_sections.keys())))
    
    for header in all_headers:
        if header not in golden_sections:
            print(f"  [-] Section MISSING in generated report: '{header}'")
            differences_found = True
            continue
        if header not in gen_sections:
            print(f"  [-] Section MISSING in baseline: '{header}'")
            differences_found = True
            continue
            
        df_gold = golden_sections[header]
        df_gen = gen_sections[header]
        
        if df_gold.shape != df_gen.shape:
            print(f"  [!] Section '{header}' DIMENSION MISMATCH:")
            print(f"      Baseline shape: {df_gold.shape} | Generated shape: {df_gen.shape}")
            differences_found = True
            continue
            
        try:
            numeric_cols = df_gold.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                gold_vals = df_gold[numeric_cols].to_numpy(dtype=float)
                gen_vals = df_gen[numeric_cols].to_numpy(dtype=float)
                
                close_mask = np.isclose(gold_vals, gen_vals, atol=tolerance, equal_nan=True)
                if not close_mask.all():
                    print(f"  [!] Section '{header}' has DATA MISMATCH in numeric values.")
                    differences_found = True
                else:
                    print(f"  [ok] Section '{header}' matched within tolerance.")
            else:
                print(f"  [ok] Section '{header}' structure verified.")
        except Exception as e:
            print(f"  [!] Error comparing data for section '{header}': {e}")
            differences_found = True

    if not differences_found:
        print(f"  [PASS] {report_name} matches baseline perfectly.")
        return True
    else:
        print(f"  [FAIL] Discrepancies detected in {report_name}.")
        return False

def run_sit_validation(baseline_dir, newreport_dir):
    """Callable function to execute SIT validation from your main pipeline."""
    log_file_path = os.path.join(baseline_dir, "SIT_Test_Results.log")
    original_stdout = sys.stdout
    tee = TeeLogger(log_file_path)
    sys.stdout = tee
    
    try:
        print(f"==================================================")
        print(f" Systems Integration Testing (SIT) Execution Log")
        print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"==================================================")
        
        # Validate Standard Report
        std_pass = compare_report_files(
            golden_path=os.path.join(baseline_dir, "Standard_Report.csv"),
            generated_path=os.path.join(newreport_dir, "Standard_Report.csv"),
            report_name="Standard Report"
        )
        
        # Validate Ratings Report
        rat_pass = compare_report_files(
            golden_path=os.path.join(baseline_dir, "Ratings_Report.csv"),
            generated_path=os.path.join(newreport_dir, "Ratings_Report.csv"),
            report_name="Ratings Report"
        )
        
        print("\n--------------------------------------------------")
        if std_pass and rat_pass:
            print("[SUCCESS] All SIT validation checks passed successfully!")
            overall_success = True
        else:
            print("[WARNING] Some SIT validation checks failed. Review logs above.")
            overall_success = False
        print("--------------------------------------------------")
        print(f"Log saved successfully to: {log_file_path}")
        
        return overall_success
        
    finally:
        sys.stdout = original_stdout
        tee.close()

if __name__ == "__main__":
    b_dir = r"C:/Users/pecen/Plexos_to_reporting/docs/Baseline Reports"
    n_dir = r"C:/Users/pecen/Downloads/"
    run_sit_validation(b_dir, n_dir)