import argparse
import os
import sys # To allow printing full traceback for debugging
import traceback # To allow printing full traceback for debugging

# Adjust Python path to include the project root directory (genealogy_analyzer)
# This allows direct execution of main.py from any location if genealogy_analyzer is in that path.
# However, it's best practice to run from the genealogy_analyzer directory itself.
# current_dir = os.path.dirname(os.path.abspath(__file__))
# if current_dir not in sys.path:
# sys.path.insert(0, current_dir)

from config_loader import load_config
from gedcom_parser import parse_gedcom
from analysis_modules import validate_formats # Uses __init__.py in analysis_modules
from reporting import generate_report # Uses __init__.py in reporting

def main():
    """
    Main function to drive the Genealogy Data Quality Assistant.
    """
    parser = argparse.ArgumentParser(
        description="Genealogy Data Quality Assistant Prototype. Analyzes GEDCOM files for formatting issues.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
    )
    parser.add_argument("gedcom_file", help="Path to the GEDCOM file to analyze.")
    parser.add_argument("-c", "--config", default=os.path.join("data", "config.json"),
                        help="Path to the JSON configuration file.")
    parser.add_argument("-o", "--output", default="genealogy_analysis_report.txt",
                        help="Path for the output analysis report file.")
    args = parser.parse_args()

    print("--- Genealogy Data Quality Assistant ---")

    gedcom_abs_path = os.path.abspath(args.gedcom_file)
    config_abs_path = os.path.abspath(args.config)
    output_abs_path = os.path.abspath(args.output)

    # 1. Load Configuration
    print(f"\n--- Loading Configuration from '{config_abs_path}' ---")
    config = load_config(args.config) # Use relative or absolute path as provided
    if not config:
        print("Exiting: Configuration loading failed.")
        return

    # 2. Parse GEDCOM File
    print(f"\n--- Parsing GEDCOM File '{gedcom_abs_path}' ---")
    gedcom_data_reader = parse_gedcom(args.gedcom_file) # Use relative or absolute
    if not gedcom_data_reader:
        print("Exiting: GEDCOM parsing failed.")
        return

    all_findings = []
    print(f"\n--- Starting Analysis Engine ---")

    # 3. Execute Analysis Modules
    print("\nRunning Format Validator...")
    try:
        format_issues = validate_formats(gedcom_data_reader, config)
        if format_issues: # Only extend if there are issues
            all_findings.extend(format_issues)
            print(f"Format Validator found {len(format_issues)} issue(s).")
        else:
            print("Format Validator found no issues.")
    except Exception as e:
        print(f"CRITICAL ERROR during Format Validation: {e}")
        traceback.print_exc()


    # (Placeholders for other analysis modules to be added in the future)
    # print("\nRunning Source Auditor...")
    # try:
    #     # from analysis_modules.source_auditor import audit_sources # Example
    #     # source_issues = audit_sources(gedcom_data_reader, config)
    #     # if source_issues: all_findings.extend(source_issues)
    #     print("Source Auditor module not yet implemented.") # Placeholder message
    # except Exception as e:
    #     print(f"CRITICAL ERROR during Source Auditing: {e}")
    #     traceback.print_exc()


    print("\n--- Analysis Phase Complete ---")
    if not all_findings:
        print("No issues found by the executed analysis modules.")
    else:
        print(f"Total issues found across all executed modules: {len(all_findings)}")

    # 4. Generate Report
    print(f"\n--- Generating Report to '{output_abs_path}' ---")
    try:
        generate_report(all_findings, gedcom_abs_path, config_abs_path, output_abs_path)
    except Exception as e:
        print(f"CRITICAL ERROR during report generation: {e}")
        traceback.print_exc()

    print("\n--- Genealogy Data Quality Assistant Finished ---")

if __name__ == "__main__":
    # This ensures that if an error occurs, the script exits with a non-zero code.
    try:
        main()
    except SystemExit as e: # Catch SystemExit from argparse (e.g. on --help)
        sys.exit(e.code)
    except Exception as e:
        print(f"An unhandled error occurred in main execution: {e}")
        traceback.print_exc()
        sys.exit(1) # Exit with a general error code
