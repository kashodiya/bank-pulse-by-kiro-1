"""Debug script to inspect H8 data download"""

import requests
import zipfile
import io

url = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&filetype=zip"

print("Downloading...")
response = requests.get(url, timeout=60)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)} bytes")

with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
    print(f"\nFiles in archive:")
    for name in zf.namelist():
        info = zf.getinfo(name)
        print(f"  {name} ({info.file_size} bytes)")
    
    # Try to read first file
    if zf.namelist():
        first_file = zf.namelist()[0]
        print(f"\nFirst 500 chars of {first_file}:")
        with zf.open(first_file) as f:
            content = f.read(500).decode('utf-8', errors='ignore')
            print(content)
