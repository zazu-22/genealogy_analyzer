# Genealogy Data Quality Assistant

This project is a prototype system designed to ingest a GEDCOM file and a user-defined ruleset (in JSON format) to analyze genealogical data for quality issues. It aims to identify inconsistencies, missing information, and formatting errors, and then generate a report of its findings.

## Project Structure

- `main.py`: The main script to orchestrate the analysis process.
- `gedcom_parser.py`: Module responsible for loading and parsing GEDCOM files using the `python-gedcom` library. It provides access to GEDCOM data elements.
- `config_loader.py`: Module for loading the analysis rules and settings from a JSON configuration file.
- `analysis_modules/`: Directory containing individual Python modules for different types of analysis:
  - `__init__.py`: Makes the `analysis_modules` directory a Python package.
  - `format_validator.py`: Checks data formats like dates, names, and places against configured rules.
  - *(Other modules like `source_auditor.py`, `consistency_checker.py` to be added later)*
- `reporting/`: Directory for modules related to generating output reports.
  - `__init__.py`: Makes the `reporting` directory a Python package.
  - `report_generator.py`: Generates a user-friendly text report of all findings.
- `data/`: Directory intended for sample data and default configurations.
  - `config.json`: The default JSON configuration file defining analysis rules.
  - `sample_format_test.ged`: A sample GEDCOM file provided for testing format validation.

## Setup

1.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv_genealogy
    ```
    Activate the environment:
    - On macOS/Linux: `source venv_genealogy/bin/activate`
    - On Windows: `venv_genealogy\Scripts\activate`

2.  **Install required Python libraries:**
    The primary dependency is `python-gedcom`.
    ```bash
    pip install python-gedcom
    ```

## Running the Assistant

Navigate to the `genealogy_analyzer` directory in your terminal.

To run the analysis with default settings (using `data/sample_format_test.ged` and `data/config.json`, outputting to `genealogy_analysis_report.txt`):

```bash
python main.py data/sample_format_test.ged
