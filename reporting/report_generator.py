import datetime
import os

def generate_report(findings, gedcom_file_path, config_file_path, output_path="genealogy_analysis_report.txt"):
    """
    Generates a simple text report from the analysis findings.

    Args:
        findings (list): A list of finding dictionaries.
        gedcom_file_path (str): Path to the analyzed GEDCOM file.
        config_file_path (str): Path to the configuration file used.
        output_path (str): The path where the report will be saved.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("--- Genealogy Data Quality Analysis Report ---\n")
            f.write(f"Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analyzed GEDCOM file: {os.path.abspath(gedcom_file_path)}\n")
            f.write(f"Configuration file used: {os.path.abspath(config_file_path)}\n")
            f.write("=" * 60 + "\n\n")

            if not findings:
                f.write("No issues found during the analysis.\n")
            else:
                f.write(f"Total issues found: {len(findings)}\n\n")
                
                findings_by_type = {}
                for finding in findings:
                    issue_type = finding.get("issue_type", "Unknown Issue Type")
                    findings_by_type.setdefault(issue_type, []).append(finding)
                
                for issue_type, type_findings in findings_by_type.items():
                    f.write(f"--- {issue_type.upper()} ({len(type_findings)} issue(s)) ---\n")
                    for i, finding in enumerate(type_findings):
                        f.write(f"  Issue {i+1}:\n")
                        f.write(f"    Record Type:       {finding.get('record_type', 'N/A')}\n")
                        f.write(f"    XREF ID:           {finding.get('element_xref_id', 'N/A')}\n")
                        f.write(f"    Tag Path:          {finding.get('element_tag_path', 'N/A')}\n")
                        f.write(f"    Problematic Value: '{finding.get('problematic_value', 'N/A')}'\n")
                        f.write(f"    Message:           {finding.get('message', 'N/A')}\n")
                        if finding.get('rule_violated'):
                            f.write(f"    Rule Violated:     {finding.get('rule_violated')}\n")
                        if finding.get('suggestion'):
                            f.write(f"    Suggestion:        {finding.get('suggestion')}\n")
                        f.write("-" * 20 + "\n")
                    f.write("\n")
            
            print(f"Report successfully generated: {os.path.abspath(output_path)}")

    except IOError as e:
        print(f"Error writing report to {os.path.abspath(output_path)}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during report generation: {e}")

if __name__ == '__main__':
    print("--- Testing Report Generator Standalone ---")
    dummy_findings = [
        {"issue_type": "Format Error", "record_type": "Individual", "element_xref_id": "@I1@",
         "element_tag_path": "INDI:@I1@/BIRT/DATE", "problematic_value": "JAN 1 1900",
         "message": "Date format error.", "suggestion": "Use DD MON YYYY."},
        {"issue_type": "Missing Info", "record_type": "Family", "element_xref_id": "@F1@",
         "element_tag_path": "FAM:@F1@/MARR", "problematic_value": "", "message": "Marriage event missing."}
    ]
    test_output = "standalone_report_test.txt"
    generate_report(dummy_findings, "dummy.ged", "dummy_config.json", test_output)
    print(f"Check {test_output} for standalone report.")
    print("--- Report Generator Standalone Test Finished ---")
