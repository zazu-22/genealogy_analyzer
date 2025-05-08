import os
from gedcom import GedcomReader
from gedcom.tags import GedcomError # Import specific GedcomError

def parse_gedcom(gedcom_file_path):
    """
    Parses a GEDCOM file and returns a GedcomReader object.
    The GedcomReader object provides access to the elements within the GEDCOM file.

    Args:
        gedcom_file_path (str): The path to the GEDCOM file.

    Returns:
        gedcom.GedcomReader: The GedcomReader object for the parsed file,
                             or None if a critical error occurs.
    """
    try:
        gedcom_reader = GedcomReader(gedcom_file_path)
        print(f"GEDCOM file '{os.path.abspath(gedcom_file_path)}' has been loaded and is ready for processing.")
        header = gedcom_reader.header_tag()
        if not header:
            print("Warning: GEDCOM header not found or could not be parsed, but processing will continue.")
        return gedcom_reader
    except FileNotFoundError:
        print(f"Error: GEDCOM file not found at {os.path.abspath(gedcom_file_path)}")
        return None
    except GedcomError as ge:
        print(f"Error parsing GEDCOM file '{os.path.abspath(gedcom_file_path)}': {ge}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while trying to read GEDCOM file '{os.path.abspath(gedcom_file_path)}': {e}")
        return None

if __name__ == '__main__':
    print("--- Testing GEDCOM Parser Standalone ---")
    # Assumes script is in genealogy_analyzer directory for this test
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    sample_gedcom_content = """
0 HEAD
1 SOUR GedcomParserTest
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR
"""
    sample_ged_path = os.path.join(data_dir, "test_standalone_parser.ged")
    with open(sample_ged_path, "w", encoding="utf-8") as f:
        f.write(sample_gedcom_content)
    print(f"Created/Updated sample GEDCOM file at {sample_ged_path}")

    gedcom_data = parse_gedcom(sample_ged_path)
    if gedcom_data:
        print("GEDCOM data loaded successfully. Accessing elements via GedcomReader:")
        header_source = "N/A"
        if gedcom_data.header_tag() and gedcom_data.header_tag().child_tag('SOUR'):
             header_source = gedcom_data.header_tag().child_tag_value('SOUR')
        print(f"Header Source: {header_source}")

        individuals_count = 0
        for element in gedcom_data.records0("INDI"):
            individuals_count +=1
            name_val = "N/A"
            xref_id = "N/A"
            if element.name_tag():
                name_val = element.name_tag().value()
            if element.xref_id():
                xref_id = element.xref_id()
            print(f"  Found Individual: {name_val} (ID: {xref_id})")
        print(f"Total individuals found: {individuals_count}")
    else:
        print(f"Failed to parse {sample_ged_path}")
    print("--- GEDCOM Parser Standalone Test Finished ---")
