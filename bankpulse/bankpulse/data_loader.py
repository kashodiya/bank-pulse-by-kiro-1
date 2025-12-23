"""Data loader for H8 Federal Reserve data"""

import requests
import zipfile
import io
from pathlib import Path
from typing import List, Dict
import pandas as pd
import xml.etree.ElementTree as ET

from .config import H8_DATA_URL, DATA_DIR
from .database import DatabaseManager


class H8DataLoader:
    """Loads and processes H8 data from Federal Reserve"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.data_dir = Path(DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_data(self) -> bytes:
        """Download H8 data zip file"""
        print(f"Downloading H8 data from {H8_DATA_URL}...")
        response = requests.get(H8_DATA_URL, timeout=60)
        response.raise_for_status()
        print("Download complete!")
        return response.content
    
    def parse_xml_data(self, xml_content: str) -> pd.DataFrame:
        """Parse XML data into DataFrame"""
        records = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Find all Series elements
            series_elements = root.findall('.//{*}Series')
            
            print(f"Found {len(series_elements)} series in XML")
            
            for series in series_elements:
                # Get series code
                series_code = series.get('SERIES_NAME') or 'Unknown'
                
                # Get series description from annotations
                series_desc = series_code
                annotations = series.findall('.//{*}Annotation')
                for annotation in annotations:
                    ann_type = annotation.find('.//{*}AnnotationType')
                    ann_text = annotation.find('.//{*}AnnotationText')
                    if ann_type is not None and ann_text is not None:
                        if 'Short Description' in ann_type.text or 'Long Description' in ann_type.text:
                            series_desc = ann_text.text
                            break
                
                # Get all observation elements
                obs_elements = series.findall('.//{*}Obs')
                
                for obs in obs_elements:
                    date = obs.get('TIME_PERIOD')
                    value = obs.get('OBS_VALUE')
                    
                    if date and value:
                        try:
                            records.append({
                                'series_name': series_desc,
                                'date': date,
                                'value': float(value),
                                'bank_type': self._extract_bank_type(series_desc),
                                'asset_class': self._extract_asset_class(series_desc)
                            })
                        except (ValueError, TypeError):
                            continue
            
            print(f"Parsed {len(records)} data points")
            
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            raise
        
        return pd.DataFrame(records)
    
    def _extract_bank_type(self, series_desc: str) -> str:
        """Extract bank type from series description"""
        desc_lower = series_desc.lower()
        if 'small' in desc_lower:
            return 'small'
        elif 'large' in desc_lower or 'domestically chartered' in desc_lower:
            return 'large'
        elif 'foreign' in desc_lower:
            return 'foreign'
        return 'all'
    
    def _extract_asset_class(self, series_desc: str) -> str:
        """Extract asset class from series description"""
        desc_lower = series_desc.lower()
        if 'commercial and industrial' in desc_lower or 'c&i' in desc_lower:
            return 'commercial_industrial'
        elif 'real estate' in desc_lower:
            return 'real_estate'
        elif 'consumer' in desc_lower:
            return 'consumer'
        elif 'deposit' in desc_lower:
            return 'deposits'
        elif 'reserve' in desc_lower:
            return 'reserves'
        elif 'loan' in desc_lower:
            return 'loans'
        return 'other'
    
    def load_and_update(self) -> Dict[str, any]:
        """Download, parse, and load H8 data into database"""
        try:
            # Download zip file
            zip_content = self.download_data()
            
            # Extract and process XML files
            all_records = []
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                xml_files = [f for f in zf.namelist() if f.endswith('.xml') and 'data' in f.lower()]
                print(f"Found {len(xml_files)} XML data files in archive")
                
                for xml_file in xml_files:
                    print(f"Processing {xml_file}...")
                    with zf.open(xml_file) as f:
                        xml_content = f.read().decode('utf-8')
                        df = self.parse_xml_data(xml_content)
                        if not df.empty:
                            all_records.append(df)
            
            # Combine all dataframes
            if all_records:
                combined_df = pd.concat(all_records, ignore_index=True)
                
                # Remove duplicates
                combined_df = combined_df.drop_duplicates(subset=['series_name', 'date'])
                
                # Insert into database
                print(f"Inserting {len(combined_df)} records into database...")
                self.db_manager.insert_data(combined_df)
                
                # Record update
                self.db_manager.record_update(len(combined_df), 'success')
                
                return {
                    'status': 'success',
                    'records_added': len(combined_df),
                    'message': f'Successfully loaded {len(combined_df)} records'
                }
            else:
                return {
                    'status': 'error',
                    'records_added': 0,
                    'message': 'No data found in archive'
                }
        
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.db_manager.record_update(0, f'error: {str(e)}')
            return {
                'status': 'error',
                'records_added': 0,
                'message': error_msg
            }
