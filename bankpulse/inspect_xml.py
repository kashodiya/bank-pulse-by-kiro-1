"""Inspect XML structure to understand series naming"""

import requests
import zipfile
import io
import xml.etree.ElementTree as ET

url = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&filetype=zip"

print("Downloading...")
response = requests.get(url, timeout=60)

with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
    # Read structure file
    print("\n=== Checking H8_struct.xml ===")
    with zf.open('H8_struct.xml') as f:
        struct_content = f.read().decode('utf-8')
        struct_root = ET.fromstring(struct_content)
        
        # Find series definitions
        series_defs = struct_root.findall('.//{*}Series')[:5]
        print(f"Found {len(struct_root.findall('.//{*}Series'))} series definitions")
        print("\nFirst 5 series:")
        for s in series_defs:
            series_id = s.get('SERIES_NAME') or s.get('id')
            # Look for description
            desc_elem = s.find('.//{*}SeriesName') or s.find('.//{*}Title') or s.find('.//{*}Description')
            desc = desc_elem.text if desc_elem is not None else "No description"
            print(f"  {series_id}: {desc}")
    
    # Check data file structure
    print("\n=== Checking H8_data.xml structure ===")
    with zf.open('H8_data.xml') as f:
        # Read just first 5000 chars
        data_sample = f.read(5000).decode('utf-8')
        print(data_sample)
