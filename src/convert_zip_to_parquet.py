import os
import shutil
import subprocess
from pathlib import Path

def find_plexos_cli():
    # 1. Check system PATH
    cli_match = shutil.which("plexos-cloud")
    if cli_match:
        return cli_match
        
    # 2. Define standard fallback paths
    search_dirs = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Energy Exemplar",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Energy Exemplar",
        Path(os.environ.get("LocalAppData", "")) / "Programs" / "Energy Exemplar"
    ]
    
    print(f"[?] Searching for 'plexos-cloud' in: {search_dirs}")
    
    for base_dir in search_dirs:
        if base_dir.exists():
            # Search for the executable
            matches = list(base_dir.rglob("plexos-cloud.exe"))
            if matches:
                print(f"[+] Found CLI at: {matches[0]}")
                return str(matches[0])
    
    print("[-] Could not find 'plexos-cloud.exe' in standard locations.")
    return None

def convert_zip_to_parquet(zip_file_path, output_dir=None, overwrite=False):
    """
    Converts PLEXOS .zip to parquet.
    
    :param zip_file_path: Path to the input zip file.
    :param output_dir: Optional custom path for output. Defaults to zip folder.
    :param overwrite: If True, deletes existing output directory before starting.
    """
    zip_path = Path(zip_file_path).resolve()
    if not zip_path.exists():
        print(f"[-] Error: File not found: {zip_path}")
        return None
        
    # Determine output directory
    if output_dir is None:
        output_dir = zip_path.parent / zip_path.stem
    else:
        output_dir = Path(output_dir)
    print(output_dir,output_dir.exists())
    # Handle existing directory
    if output_dir.exists():
        print('here')
        if overwrite:
            print('if')
            print(f"[!] Overwrite enabled. Removing existing: {output_dir}")
            shutil.rmtree(output_dir)
        else:
            print('else')
            print(f"[~] Directory exists. Skipping: {output_dir}")
            return output_dir
            
    # Locate CLI
    plexos_cli_path = find_plexos_cli()
    if not plexos_cli_path:
        print("[-] Error: 'plexos-cloud' CLI not found.")
        return None
    
    # Construct arguments as a LIST (No manual quoting needed)
    cmd = [
        plexos_cli_path, "solution", "convert", "zip-to-parquet",
        "--zipPath", str(zip_path),
        "-d", str(output_dir)
    ]
    
    print(f"[+] Executing: {' '.join(cmd)}")
    
    try:
        # Use shell=False (default) and pass the list
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[+] Conversion completed.")
        return output_dir
    except subprocess.CalledProcessError as e:
        print(f"[-] CLI Error: {e.stderr}")
        return None