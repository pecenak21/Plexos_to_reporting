import pandas as pd
import numpy as np
import os
import io
import sys
import contextlib
import traceback
from collections import Counter
from datetime import datetime

class TeeLogger:
    """Helper class to simultaneously print to the terminal and write to a log file."""
    def __init__(self, log, terminal):
        self.terminal = terminal
        self.log = log

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()


@contextlib.contextmanager
def tee_output(filename):
    """Copy everything printed to stdout and stderr (tracebacks included) into `filename`.

    Nests: an inner tee writes through the outer one, so its lines land in both logs.
    """
    original_stdout, original_stderr = sys.stdout, sys.stderr
    with open(filename, 'w', encoding='utf-8') as log:
        sys.stdout = TeeLogger(log, original_stdout)
        sys.stderr = TeeLogger(log, original_stderr)
        try:
            yield
        except BaseException:
            # Python prints the traceback to the console only after the stack has unwound,
            # by which point this log is closed -- so copy it into the log file here.
            log.write(traceback.format_exc())
            raise
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr

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

def _diff_section_headers(golden_sections, gen_sections):
    """Check 1: the same set of section headers exists in both reports."""
    golden_headers = set(golden_sections.keys())
    gen_headers = set(gen_sections.keys())
    missing_in_gen = sorted(golden_headers - gen_headers)
    missing_in_gold = sorted(gen_headers - golden_headers)

    if missing_in_gen:
        print(f"  [-] {len(missing_in_gen)} section(s) in baseline but MISSING from generated report:")
        for h in missing_in_gen:
            print(f"        '{h}'")
    if missing_in_gold:
        print(f"  [-] {len(missing_in_gold)} section(s) in generated report but MISSING from baseline:")
        for h in missing_in_gold:
            print(f"        '{h}'")

    common_headers = sorted(golden_headers & gen_headers)
    return (not missing_in_gen and not missing_in_gold), common_headers


def _diff_row_labels(header, df_gold, df_gen):
    """Check 2: the row label (index) column matches between the two sections.

    Compared as a multiset (via Counter) rather than a plain set so duplicate
    labels -- which occur by design in nested/bespoke blocks that repeat
    '(Primary)'/'(Secondary)' style sub-rows per generator -- are counted, not
    just checked for presence (this also catches an accidentally-duplicated
    row). Blank labels (spacer rows within nested blocks) carry no identifying
    information and are excluded.
    """
    gold_labels = Counter(str(x) for x in df_gold.index if pd.notna(x) and str(x).strip() != '')
    gen_labels = Counter(str(x) for x in df_gen.index if pd.notna(x) and str(x).strip() != '')

    mismatches = [
        (label, gold_labels.get(label, 0), gen_labels.get(label, 0))
        for label in sorted(set(gold_labels) | set(gen_labels))
        if gold_labels.get(label, 0) != gen_labels.get(label, 0)
    ]

    if mismatches:
        print(f"  [!] Section '{header}' ROW LABEL MISMATCH ({len(mismatches)} label(s)):")
        for label, gc, nc in mismatches:
            if nc == 0:
                print(f"        MISSING from generated: '{label}' (baseline has {gc}x)")
            elif gc == 0:
                print(f"        EXTRA in generated: '{label}' (not in baseline, found {nc}x)")
            else:
                print(f"        COUNT MISMATCH: '{label}' -- baseline={gc}x, generated={nc}x")

    return not mismatches


def _diff_data(header, df_gold, df_gen, tolerance, top_n_magnitude=3):
    """Check 3: shape, then -- if shapes match -- a tolerance-gated, magnitude-ranked value diff."""
    if df_gold.shape != df_gen.shape:
        print(f"  [!] Section '{header}' DIMENSION MISMATCH:")
        print(f"      Baseline shape: {df_gold.shape} | Generated shape: {df_gen.shape}")
        return False

    numeric_cols = df_gold.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        print(f"  [ok] Section '{header}' structure verified.")
        return True

    # Align rows by label when both sides carry a unique, matching label set, so a row
    # reorder (e.g. a query gaining an ORDER BY) doesn't masquerade as a data mismatch.
    if df_gold.index.is_unique and df_gen.index.is_unique and set(df_gold.index) == set(df_gen.index):
        df_gen = df_gen.reindex(df_gold.index)

    try:
        gold_vals = df_gold[numeric_cols].to_numpy(dtype=float)
        gen_vals = df_gen[numeric_cols].to_numpy(dtype=float)
    except Exception as e:
        print(f"  [!] Error comparing data for section '{header}': {e}")
        return False

    close_mask = np.isclose(gold_vals, gen_vals, atol=tolerance, equal_nan=True)
    if close_mask.all():
        print(f"  [ok] Section '{header}' matched within tolerance.")
        return True

    # Rank mismatches by order-of-magnitude (how many multiples apart the two values are)
    # rather than raw absolute difference -- a 10x/100x jump usually means a real bug
    # (wrong unit conversion, wrong aggregation), and is far more diagnostic than a pile
    # of rounding-level misses. Only the worst few are printed; the rest are just counted.
    floor = 1e-9
    mismatch_idx = np.argwhere(~close_mask)
    scored = []
    for r, c in mismatch_idx:
        g, n = gold_vals[r, c], gen_vals[r, c]
        abs_diff = abs(n - g)
        magnitude = (max(abs(g), abs(n)) + floor) / (min(abs(g), abs(n)) + floor)
        scored.append((magnitude, abs_diff, r, c, g, n))
    scored.sort(key=lambda x: (-x[0], -x[1]))

    print(f"  [!] Section '{header}': {len(scored)} of {gold_vals.size} cell(s) outside tolerance "
          f"({tolerance}). Top {min(top_n_magnitude, len(scored))} by magnitude:")
    for magnitude, abs_diff, r, c, g, n in scored[:top_n_magnitude]:
        row_label = df_gold.index[r]
        col_label = numeric_cols[c]
        print(f"        Row '{row_label}', Col '{col_label}': baseline={g:.4f}, generated={n:.4f} "
              f"(diff={abs_diff:.4f}, {magnitude:.1f}x)")

    return False


def compare_report_files(golden_path, generated_path, report_name="Report", tolerance=2e-4, top_n_magnitude=3):
    # Report values are rounded to 4 decimals on export (export_block_to_csv), but DuckDB's
    # parallel SUM aggregation is not bit-deterministic across runs of identical data -- summation
    # order noise on the order of 1e-10 can flip the last rounded digit (e.g. 0.5761 vs 0.5762).
    # A tolerance tighter than the export rounding grid (1e-4) flags that noise as a mismatch, so
    # this must stay looser than 1e-4 to avoid flaky failures unrelated to real data regressions.
    print(f"\n[+] Running SIT Semantic Diff for: {report_name}")
    print(f"    Baseline:  {golden_path}")
    print(f"    Generated: {generated_path}")

    golden_sections = parse_report_into_sections(golden_path)
    gen_sections = parse_report_into_sections(generated_path)

    if not golden_sections or not gen_sections:
        print(f"  [FAIL] Could not parse sections for {report_name}.")
        return False

    # 1. Section headers
    headers_ok, common_headers = _diff_section_headers(golden_sections, gen_sections)
    differences_found = not headers_ok

    for header in common_headers:
        df_gold = golden_sections[header]
        df_gen = gen_sections[header]

        # 2. Row labels
        labels_ok = _diff_row_labels(header, df_gold, df_gen)

        # 3. Shape, then magnitude-ranked value diff
        data_ok = _diff_data(header, df_gold, df_gen, tolerance, top_n_magnitude)

        if not (labels_ok and data_ok):
            differences_found = True

    if not differences_found:
        print(f"  [PASS] {report_name} matches baseline perfectly.")
        return True
    else:
        print(f"  [FAIL] Discrepancies detected in {report_name}.")
        return False

def run_sit_validation(baseline_dir, newreport_dir):
    """Callable function to execute SIT validation from your main pipeline.

    The log is written beside the generated reports, not into the baseline folder, so
    each run keeps its own record and the checked-in baselines are never touched.
    """
    log_file_path = os.path.join(newreport_dir, "SIT_Test_Results.log")

    with tee_output(log_file_path):
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

if __name__ == "__main__":
    from create_reports import load_excel_config

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    baseline_dir = os.path.join(repo_root, "docs", "Baseline Reports")

    config_path = sys.argv[1] if len(sys.argv) > 1 else 'report_config.xlsx'
    (blueprint, blueprint_rat, asset_groups, input_path, cli_path, base_output_path,
     df_units, script_path, asset_mapping, contract_rows) = load_excel_config(config_path)

    run_sit_validation(baseline_dir, base_output_path)