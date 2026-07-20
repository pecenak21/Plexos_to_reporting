# PLEXOS Reporting Automation Engine

A flexible, Python-based automation framework designed to transform PLEXOS solution files into standardized resource planning reports. This tool bridges the gap between raw PLEXOS output and the specific formatting requirements of the resource planning team, using an Excel-driven configuration interface.

## Features
*   **Excel-Driven Configuration:** Easily define file paths, data extraction parameters, unit conversions, and reporting subsets directly via the `PLEXOS Reporting Template` Excel workbook.
*   **Standardized Reporting:** Automates the creation of two core reports, ensuring alignment with the team's existing reporting structure.
*   **Flexible Metric Management:** Designed for modularity; add or modify metrics without needing to rewrite core data processing logic.
*   **Dynamic Filtering:** Supports filtering of generator subsets (e.g., thermal, renewable) through the control workbook.
*   **Built-in Data Integration:** Currently utilizes the PLEXOS-provided Parquet converter (transitioning to native PLEXOS Parquet output in future iterations).

## Tech Stack
*   **Language:** Python 3.7+ (3.12 recommended)
*   **Interface:** Excel / VBA (Background execution)
*   **Core Dependencies:** `pandas`, `pyarrow` (via PLEXOS CLI/Parquet utilities) — *See `requirements.txt` for the full list.*
*   **Source:** Git (Version Control)

## Getting Started

### Prerequisites
1.  **Python Environment:** Ensure you have Python 3.7 or greater installed (3.12 is recommended).
2.  **Dependencies:** Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  **PLEXOS CLI:** Ensure the `plexos-cli` parquet converter is available.
    *   [Download PLEXOS CLI Converter](https://marketplace-ui-eeprod-na.energyexemplar.com/market/global/d1cd2867-7586-47fe-a9ab-1464d2617f61?tab=overview&source=)

### Setup
1.  **Repository:** Clone this repository to your local machine or shared development environment.
2.  **Configuration:** The project is designed to point to external data sources (e.g., NAS/H-Drive storage). Ensure your machine has the necessary read/write permissions to the relevant directories.
3.  **Execution:** Open the `PLEXOS Reporting Template.xlsm` workbook. The embedded VBA macro manages the background execution of the Python scripts once paths and parameters are configured.

## Usage
The workflow is managed entirely through the Excel template:
1.  **Define Inputs:** Input the path to your PLEXOS solution file in the designated cell.
2.  **Configure Outputs:** Utilize the Excel interface to select the data metrics to pull and specify any necessary unit conversions.
3.  **Run:** Trigger the VBA macro to execute the conversion. The Python script will read the configuration, process the data, and generate the required report files.

## Project Structure
*   `src/`: Core Python logic and data processing scripts.
*   `docs/`: Additional documentation and requirements tracking.
*   `template/`: The `PLEXOS Reporting Template.xlsm` controller.
*   `requirements.txt`: List of required Python environment packages.

## Contributing
We welcome contributions to refine the reporting structure or improve performance. Changes are managed via Git:
1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a pull request for review by the team.

## License
This project is open-source and intended for internal team utility.