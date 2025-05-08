import datetime
import re
import os
import sys # For standalone testing path adjustments

# --- Helper function to create standardized issue dictionaries ---
def _create_finding(issue_type, record_type, element_xref_id, element_tag_path, problematic_value, message, rule_violated=None, suggestion=None):
    """Helper function to create a standardized finding dictionary."""
    finding = {
        "issue_type": issue_type,
        "record_type": record_type,
        "element_xref_id": element_xref_id,
        "element_tag_path": element_tag_path,
        "problematic_value": problematic_value,
        "message": message
    }
    if rule_violated:
        finding["rule_violated"] = rule_violated
    if suggestion:
        finding["suggestion"] = suggestion
    return finding

# --- Date Validation Logic ---
def _is_date_parsable(single_date_str, preferred_formats):
    """Attempts to parse a single date component against preferred formats."""
    if not single_date_str:
        return False
    for fmt in preferred_formats:
        try:
            datetime.datetime.strptime(single_date_str.strip(), fmt)
            return True
        except ValueError:
            continue
    return False

def _validate_date_value(date_str, preferred_formats):
    """
    Validates a date string against a list of preferred formats.
    Handles common GEDCOM date qualifiers and "BET...AND..." ranges.
    Returns True if valid, False otherwise.
    """
    if not date_str: # An empty date string itself is not a format error for this validator
        return True 

    original_date_str_upper = date_str.upper()
    # Use original_date_str for re.match to preserve case for group extraction if needed, though IGNORECASE is used
    cleaned_date_str = date_str # Will be modified if prefixes are stripped

    # Handle "BET <date1> AND <date2>"
    if original_date_str_upper.startswith("BET ") and " AND " in original_date_str_upper:
        try:
            # Regex to capture date1 and date2 from "BET date1 AND date2"
            match = re.match(r"BET (.*) AND (.*)", date_str, re.IGNORECASE)
            if match:
                date1_str = match.group(1).strip()
                date2_str = match.group(2).strip()
                # Validate each part of the BET...AND date.
                if _is_date_parsable(date1_str, preferred_formats) and \
                   _is_date_parsable(date2_str, preferred_formats):
                    return True
                else: # One or both parts of BET...AND are not parsable
                    return False 
            else: # Regex didn't match the expected BET...AND structure (e.g. "BET date1AND date2")
                return False
        except Exception: # Broad catch for any error during BET...AND parsing
            return False


    # Strip common prefixes for single dates or BEF/AFT/ABT etc. dates
    prefixes_to_strip = ["ABT ", "CAL ", "EST ", "INT ", "BEF ", "AFT ", "FROM ", "TO "]
    # Check original_date_str_upper for prefix, but strip from date_str to maintain original case for parsing
    prefix_found = False
    for prefix in prefixes_to_strip:
        if original_date_str_upper.startswith(prefix):
            cleaned_date_str = date_str[len(prefix):]
            prefix_found = True
            break 

    # Attempt to parse the (potentially cleaned) date string
    if _is_date_parsable(cleaned_date_str, preferred_formats):
        return True
        
    # If a prefix was stripped AND it still failed, it's an error.
    # If no prefix was stripped AND it failed, it's an error.
    return False

# --- Place Validation Logic ---
def _validate_place_structure(place_str, expected_structures):
    """
    Validates a place string against expected comma-separated structures.
    This is a basic heuristic check based on the number of comma-separated parts.
    Returns True if it *could* match one of the structures or is empty, False otherwise.
    """
    if not place_str: # An empty place string is not a format error
        return True 

    num_parts = len(place_str.split(','))

    for struct_str in expected_structures:
        expected_num_parts = len(struct_str.split(','))
        if num_parts == expected_num_parts:
            return True 
            
    if num_parts == 1 and any(len(s.split(',')) == 1 for s in expected_structures):
        return True
        
    return False


# --- Main Validation Function ---
def validate_formats(gedcom_reader, config):
    """
    Validates formats for names, dates, and places in the GEDCOM data.
    """
    findings = []
    
    preferred_date_formats = config.get("preferred_date_formats", [])
    expected_place_structures = config.get("expected_place_format_structures", [])
    enforce_surname_slashes = config.get("name_validation_rules", {}).get("enforce_surname_slashes", True)

    for indi_element in gedcom_reader.records0("INDI"):
        indi_id = indi_element.xref_id() if indi_element.xref_id() else "UNKNOWN_INDI"
        element_tag_path_base = f"INDI:{indi_id}"

        name_tag = indi_element.child_tag("NAME")
        if name_tag:
            name_value_raw = name_tag.value() 
            name_value_stripped = name_value_raw.strip()

            if not name_value_stripped or name_value_stripped == '/' or name_value_stripped == '//':
                findings.append(_create_finding(
                    "Format Error", "Individual", indi_id, f"{element_tag_path_base}/NAME", 
                    name_value_raw, "Name is missing or appears to be empty."))
            elif enforce_surname_slashes:
                parsed_surname = name_tag.surname()
                if not parsed_surname and "/" not in name_value_raw:
                     findings.append(_create_finding(
                        "Format Error", "Individual", indi_id, f"{element_tag_path_base}/NAME", name_value_raw,
                        "Name does not appear to use standard GEDCOM surname slashes (e.g., First /Surname/).",
                        suggestion="Ensure surname is enclosed in slashes like /SURNAME/."))
                elif "/" in name_value_raw and not parsed_surname and name_value_raw.count("/") >= 2:
                    # Slashes present, but couldn't parse surname (e.g. "Name / /")
                    findings.append(_create_finding(
                        "Format Error", "Individual", indi_id, f"{element_tag_path_base}/NAME", name_value_raw,
                        "Name contains slashes, but surname part might be empty or malformed (e.g., 'Name / /').",
                        suggestion="Check surname formatting between slashes."))
        
        event_tags_to_check = ["BIRT", "DEAT", "CHR", "ADOP", "BURI", "EVEN"] 
        for event_tag_str in event_tags_to_check:
            for event_element in indi_element.children_tags(event_tag_str):
                event_path_base_specific = f"{element_tag_path_base}/{event_element.tag()}"
                
                date_tag = event_element.child_tag("DATE")
                if date_tag and date_tag.value():
                    date_val = date_tag.value().strip()
                    if date_val and not _validate_date_value(date_val, preferred_date_formats):
                        findings.append(_create_finding(
                            "Format Error", "Event (Individual)", indi_id, f"{event_path_base_specific}/DATE", date_val,
                            f"Date format for {event_element.tag()} ('{date_val}') invalid.", "preferred_date_formats",
                            f"Supported formats: {', '.join(preferred_date_formats)} or GEDCOM date phrases (ABT, BEF, BET...AND...)."))

                place_tag = event_element.child_tag("PLAC")
                if place_tag and place_tag.value():
                    place_val = place_tag.value().strip()
                    if place_val and not _validate_place_structure(place_val, expected_place_structures):
                        findings.append(_create_finding(
                            "Format Error", "Event (Individual)", indi_id, f"{event_path_base_specific}/PLAC", place_val,
                            f"Place format for {event_element.tag()} ('{place_val}') does not match expected structures based on comma count.",
                            "expected_place_format_structures",
                            f"Expected parts (by comma count): {len(expected_place_structures[0].split(','))} for '{expected_place_structures[0]}' etc."))
                        
    for fam_element in gedcom_reader.records0("FAM"):
        fam_id = fam_element.xref_id() if fam_element.xref_id() else "UNKNOWN_FAM"
        element_tag_path_base = f"FAM:{fam_id}"

        family_event_tags_to_check = ["MARR", "DIV", "ANUL", "ENGA", "EVEN"]
        for event_tag_str in family_event_tags_to_check:
            for event_element in fam_element.children_tags(event_tag_str):
                event_path_base_specific = f"{element_tag_path_base}/{event_element.tag()}"

                date_tag = event_element.child_tag("DATE")
                if date_tag and date_tag.value():
                    date_val = date_tag.value().strip()
                    if date_val and not _validate_date_value(date_val, preferred_date_formats):
                        findings.append(_create_finding(
                            "Format Error", "Event (Family)", fam_id, f"{event_path_base_specific}/DATE", date_val,
                            f"Date format for {event_element.tag()} ('{date_val}') invalid.", "preferred_date_formats",
                            f"Supported formats: {', '.join(preferred_date_formats)} or GEDCOM date phrases."))
                
                place_tag = event_element.child_tag("PLAC")
                if place_tag and place_tag.value():
                    place_val = place_tag.value().strip()
                    if place_val and not _validate_place_structure(place_val, expected_place_structures):
                        findings.append(_create_finding(
                            "Format Error", "Event (Family)", fam_id, f"{event_path_base_specific}/PLAC", place_val,
                            f"Place format for {event_element.tag()} ('{place_val}') does not match structures based on comma count.",
                            "expected_place_format_structures",
                            f"Expected parts (by comma count): {len(expected_place_structures[0].split(','))} for '{expected_place_structures[0]}' etc."))
    return findings

if __name__ == '__main__':
    print("--- Testing Format Validator Standalone ---")
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir)) # Up to genealogy_analyzer
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from genealogy_analyzer.gedcom_parser import parse_gedcom
    from genealogy_analyzer.config_loader import load_config
    import json

    default_config_path = os.path.join(project_root, "data", "config.json") # Use the main config
    # Create a specific GEDCOM for this validator's test, not the generic sample_format_test.ged
    validator_test_gedcom_path = os.path.join(project_root, "data", "validator_standalone_test.ged") 
    data_dir_for_test = os.path.join(project_root, "data") # Ensure data dir exists

    # Ensure config.json exists for the test, or create a default one
    if not os.path.exists(default_config_path):
        print(f"Warning: Main config file {default_config_path} not found for standalone test. Creating a temporary one.")
        os.makedirs(data_dir_for_test, exist_ok=True)
        temp_test_config_data = {
            "preferred_date_formats": ["%d %b %Y", "%Y-%m-%d", "%b %Y", "%Y", "%d/%m/%Y"],
            "expected_place_format_structures": ["City, State, Country", "City, Country", "Country"],
            "name_validation_rules": {"enforce_surname_slashes": True} 
        }
        with open(default_config_path, 'w') as cf_temp:
            json.dump(temp_test_config_data, cf_temp, indent=2)

    validator_test_gedcom_content = """
0 HEAD
1 SOUR ValidatorTest
0 @I1@ INDI
1 NAME John /Doe/
1 BIRT
2 DATE 1 JAN 1900
0 @I2@ INDI
1 NAME Jane Smith /* No slashes */
1 BIRT
2 DATE BET 1 MAR 1990 AND 5 MAR 1990
0 @I3@ INDI
1 NAME /EmptySlashes/
1 DEAT
2 DATE 32 MAR 2000 /* Invalid day */
0 @I4@ INDI
1 NAME Two /Slashes/ Here /Again/ /* Multiple Slashes, should be handled by name_tag.surname() */
1 BIRT
2 DATE ABT 1950
0 @I5@ INDI
1 NAME MissingDatePerson /Family/
1 BIRT
2 PLAC SomeCity, SomeState, SomeCountry
0 @I6@ INDI
1 NAME Bad /DateRange/
1 BIRT
2 DATE BET 1 JAN 2000 AND UNKNOWN
0 TRLR
"""
    with open(validator_test_gedcom_path, "w", encoding="utf-8") as f_ged:
        f_ged.write(validator_test_gedcom_content)
    print(f"Created/Updated GEDCOM for validator testing at {validator_test_gedcom_path}")
    
    config_for_test = load_config(default_config_path)
    gedcom_reader_for_test = parse_gedcom(validator_test_gedcom_path)

    if gedcom_reader_for_test and config_for_test:
        print("\n--- Running Validation (Standalone Test) ---")
        findings = validate_formats(gedcom_reader_for_test, config_for_test)
        if findings:
            print(f"\nFound {len(findings)} format issues in standalone test:")
            for i, finding in enumerate(findings):
                print(f"  {i+1}. {finding['message']} (Value: '{finding['problematic_value']}' at {finding['element_tag_path']})")
        else:
            print("No format issues found in standalone test.")
    else:
        if not gedcom_reader_for_test: print("Failed to load GEDCOM for standalone test.")
        if not config_for_test: print("Failed to load CONFIG for standalone test.")
    print("\n--- Format Validator Standalone Test Finished ---")
